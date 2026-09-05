"""Hardened HTTP client shared by every KPL scraper.

Both upstream sources are small, self-hosted sites (LiteSpeed / Apache on a
single box). Hammering them is the fastest way to get the workers throttled or
blocked, so this module centralises the things that keep the scrapers polite and
the workers stable:

* explicit connect/read timeouts (a hung socket used to wedge a worker slot);
* bounded retries with exponential backoff + jitter on transient failures only;
* a per-host politeness delay so concurrent tasks cannot burst the same origin;
* conditional GETs (ETag / Last-Modified) cached in Redis, so an unchanged page
  costs a 304 instead of a full download;
* one connection-pooled ``Session`` per process instead of a socket per call.

Everything raises :class:`SourceUnavailable` on transient trouble so callers can
apply a single retry policy.
"""

from __future__ import annotations

import logging
import random
import threading
import time
from dataclasses import dataclass
from typing import Dict, Optional
from urllib.parse import urlparse

import requests
from django.core.cache import cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import SourceUnavailable

logger = logging.getLogger(__name__)

# (connect, read). Connect is short — a source that will not answer the
# handshake is down. Read is generous: the largest page is a few hundred KB of
# server-rendered HTML and is slow under load.
DEFAULT_TIMEOUT = (10, 45)

DEFAULT_HOST_DELAY = 1.5

# Anything smaller is a parked page, an error page, or a truncated response —
# never a real data page.
MIN_HTML_BYTES = 1500

USER_AGENTS = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
)

_local = threading.local()
_host_lock = threading.Lock()
_last_request_at: Dict[str, float] = {}


@dataclass(frozen=True)
class Response:
    """A fetched page plus the metadata needed to skip it next time."""

    url: str
    status_code: int
    text: str
    from_cache: bool = False

    @property
    def not_modified(self) -> bool:
        return self.status_code == 304


def _build_session() -> requests.Session:
    session = requests.Session()

    # urllib3 handles the transport-level retries (connect errors, 429, 5xx).
    # Anything it gives up on surfaces as a RequestException and becomes a
    # SourceUnavailable for the Celery-level retry to deal with.
    retry = Retry(
        total=3,
        connect=3,
        read=2,
        status=3,
        backoff_factor=1.5,
        status_forcelist=(408, 429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "HEAD"}),
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=8, pool_maxsize=8)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def get_session() -> requests.Session:
    """Return this thread's pooled session, creating it on first use."""
    session = getattr(_local, "session", None)
    if session is None:
        session = _build_session()
        _local.session = session
    return session


def _throttle(host: str, delay: float) -> None:
    """Sleep just long enough that this host is not hit faster than ``delay``."""
    with _host_lock:
        last = _last_request_at.get(host)
        now = time.monotonic()
        if last is not None:
            wait = delay - (now - last)
            if wait > 0:
                # Jitter stops two workers releasing in lockstep.
                time.sleep(wait + random.uniform(0, 0.4))
        _last_request_at[host] = time.monotonic()


def _validator_cache_key(url: str) -> str:
    return f"kpl:scrape:validators:{url}"


def fetch(
    url: str,
    *,
    timeout: tuple = DEFAULT_TIMEOUT,
    host_delay: float = DEFAULT_HOST_DELAY,
    use_conditional: bool = True,
    min_bytes: int = MIN_HTML_BYTES,
    extra_headers: Optional[Dict[str, str]] = None,
) -> Response:
    """GET ``url`` politely and return the body.

    Raises:
        SourceUnavailable: on network failure, non-2xx status, or a body too
            short to be a real page.
    """
    host = urlparse(url).netloc.lower()
    _throttle(host, host_delay)

    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.9",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    if extra_headers:
        headers.update(extra_headers)

    validators = cache.get(_validator_cache_key(url)) if use_conditional else None
    if validators:
        if validators.get("etag"):
            headers["If-None-Match"] = validators["etag"]
        if validators.get("last_modified"):
            headers["If-Modified-Since"] = validators["last_modified"]

    started = time.monotonic()
    try:
        response = get_session().get(url, headers=headers, timeout=timeout)
    except requests.RequestException as exc:
        raise SourceUnavailable(f"GET {url} failed: {exc}") from exc

    elapsed = time.monotonic() - started

    if response.status_code == 304:
        logger.info("GET %s -> 304 not modified (%.2fs)", url, elapsed)
        return Response(url=url, status_code=304, text="", from_cache=True)

    if response.status_code >= 400:
        raise SourceUnavailable(f"GET {url} returned HTTP {response.status_code}")

    # Some upstream pages do not declare a charset;
    # requests then guesses ISO-8859-1 and mangles player names.
    if not response.encoding or response.encoding.lower() == "iso-8859-1":
        response.encoding = response.apparent_encoding or "utf-8"

    body = response.text
    if len(body) < min_bytes:
        raise SourceUnavailable(
            f"GET {url} returned only {len(body)} bytes "
            f"(expected at least {min_bytes}); source is likely parked or erroring"
        )

    if use_conditional:
        etag = response.headers.get("ETag")
        last_modified = response.headers.get("Last-Modified")
        if etag or last_modified:
            cache.set(
                _validator_cache_key(url),
                {"etag": etag, "last_modified": last_modified},
                timeout=60 * 60 * 24 * 7,
            )

    logger.info(
        "GET %s -> %s, %s bytes (%.2fs)",
        url,
        response.status_code,
        len(body),
        elapsed,
    )
    return Response(url=url, status_code=response.status_code, text=body)


def fetch_json(url: str, **kwargs):
    """GET ``url`` and decode JSON, mapping decode failures to SourceUnavailable."""
    kwargs.setdefault("min_bytes", 2)
    kwargs.setdefault("extra_headers", {"Accept": "application/json"})
    response = fetch(url, **kwargs)
    if response.not_modified:
        return None
    try:
        import json

        return json.loads(response.text)
    except ValueError as exc:
        raise SourceUnavailable(f"GET {url} returned non-JSON body: {exc}") from exc


def fetch_bytes(url: str, *, timeout: tuple = DEFAULT_TIMEOUT, max_bytes: int = 5_000_000):
    """Download a binary asset (used for team logos), capped at ``max_bytes``."""
    host = urlparse(url).netloc.lower()
    _throttle(host, DEFAULT_HOST_DELAY)
    headers = {"User-Agent": random.choice(USER_AGENTS), "Accept": "image/*,*/*;q=0.8"}
    try:
        response = get_session().get(url, headers=headers, timeout=timeout, stream=True)
        response.raise_for_status()
        chunks = bytearray()
        for chunk in response.iter_content(64 * 1024):
            chunks.extend(chunk)
            if len(chunks) > max_bytes:
                raise SourceUnavailable(f"{url} exceeded {max_bytes} bytes")
        return bytes(chunks), response.headers.get("Content-Type", "")
    except requests.RequestException as exc:
        raise SourceUnavailable(f"GET {url} failed: {exc}") from exc
