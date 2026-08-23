"""Regression test: nginx must reject requests whose Host header is not one of
the site's domains before they reach Django.

Without a catch-all ``default_server``, the port-443 server block (the only one
on that port) is nginx's implicit default, so any request whose Host does not
match its ``server_name`` -- e.g. ``forum.fantasykenya.com`` from a scanner or a
stale DNS record -- was still proxied to the API with the original Host header
preserved (``proxy_set_header Host $host``). Django then raised
``DisallowedHost`` and logged an ERROR for every probe. The ``default_server``
block closes the connection instead, keeping Django's ``ALLOWED_HOSTS`` check
as a second line of defence rather than the first.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
NGINX_CONF = REPO_ROOT / "docker" / "production" / "nginx" / "nginx.conf"


def test_nginx_rejects_unmatched_hosts_before_django():
    body = NGINX_CONF.read_text()

    # A catch-all default server must exist for both ports the proxy listens on.
    assert "listen 80 default_server" in body
    assert "listen 443 ssl default_server" in body
    assert "server_name _;" in body

    # It must drop the connection instead of proxying to Django.
    assert "return 444;" in body
