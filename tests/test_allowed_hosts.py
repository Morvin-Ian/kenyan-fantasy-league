"""Regression test: production must never serve every Host, or none.

``config/settings/base.py`` reads ALLOWED_HOSTS from the environment and falls
back to ``"*"`` when the variable is unset, so that development and CI keep
working without one. Production inherited that fallback: nothing in the
repository set the variable — not ``.env.example``, not
``docker-compose.prod.yml`` — so whether production accepted arbitrary Host
headers depended entirely on a gitignored file nobody could check.

The other half is quieter. A ``.env.prod`` copied from ``.env.example`` has
``ALLOWED_HOSTS=`` with no value, and an empty string is *set*, so the ``"*"``
default never applies: the list parses to ``[]`` and Django rejects every
request with DisallowedHost.

Both are silent. With SECURE_HSTS_PRELOAD on and USE_X_FORWARDED_HOST trusting
the proxy, a wildcard lets a poisoned Host header into the activation and
password-reset links this app builds.
"""

import pathlib
import re

from config.settings.production import ALLOWED_HOSTS, SERVED_DOMAINS, pinned_hosts


def test_production_never_serves_every_host():
    """The wildcard is the thing this whole module exists to prevent."""
    assert "*" not in ALLOWED_HOSTS


def test_production_serves_something():
    """An empty list rejects every request — an outage, not a safeguard."""
    assert ALLOWED_HOSTS


def test_the_fallback_is_the_domains_nginx_actually_serves():
    """If the two drift apart, the fallback silently stops being a fallback:
    Django would refuse the hosts nginx forwards. Read from nginx.conf rather
    than restated, so moving domains has to move both."""
    conf = (
        pathlib.Path(__file__).resolve().parents[1]
        / "docker"
        / "production"
        / "nginx"
        / "nginx.conf"
    ).read_text()
    served = set()
    for match in re.finditer(r"^\s*server_name\s+([^;]+);", conf, re.MULTILINE):
        names = set(match.group(1).split())
        if names != {"_"}:
            served.update(names)

    assert served, "no application server_name in nginx.conf — has the file moved?"
    assert set(SERVED_DOMAINS) == served


def test_unrecognised_hosts_are_rejected_by_nginx_before_django():
    """A default server must not proxy scanner Host headers to the API."""
    conf = (
        pathlib.Path(__file__).resolve().parents[1]
        / "docker"
        / "production"
        / "nginx"
        / "nginx.conf"
    ).read_text()

    assert re.search(r"listen 80 default_server;\s+server_name _;\s+return 444;", conf)
    assert re.search(
        r"listen 443 ssl default_server;[\s\S]*?server_name _;[\s\S]*?return 444;",
        conf,
    )


def test_an_unset_variable_falls_back_to_the_real_domains():
    """Unset reaches production.py as base.py's ["*"]."""
    assert pinned_hosts(["*"], SERVED_DOMAINS) == SERVED_DOMAINS


def test_a_blank_variable_falls_back_rather_than_locking_everyone_out():
    """Blank reaches production.py as [], which would refuse every request."""
    assert pinned_hosts([], SERVED_DOMAINS) == SERVED_DOMAINS


def test_a_configured_value_is_used_as_given():
    """Pinning is a floor, not an override: staging can name its own host."""
    assert pinned_hosts(["staging.fantasykenya.com"], SERVED_DOMAINS) == [
        "staging.fantasykenya.com"
    ]


def test_a_wildcard_mixed_with_real_hosts_loses_the_wildcard():
    """ "*, fantasykenya.com" is still a wildcard — the rest is decoration."""
    assert pinned_hosts(["*", "fantasykenya.com"], SERVED_DOMAINS) == [
        "fantasykenya.com"
    ]


def test_the_fallback_cannot_be_mutated_through_the_result():
    """A caller editing its ALLOWED_HOSTS must not rewrite SERVED_DOMAINS."""
    result = pinned_hosts([], SERVED_DOMAINS)
    result.append("evil.example")
    assert "evil.example" not in SERVED_DOMAINS


def test_default_tls_server_rejects_unknown_hosts_before_django():
    """Host-header probes must not create Django DisallowedHost log entries."""
    conf = (
        pathlib.Path(__file__).resolve().parents[1]
        / "docker"
        / "production"
        / "nginx"
        / "nginx.conf"
    ).read_text()

    assert "if ($host !~ ^(fantasykenya\\.com|www\\.fantasykenya\\.com)$) {" in conf
    assert "return 444;" in conf


def test_kfl_proxy_does_not_forward_a_host_from_an_upstream_proxy():
    """Django must validate the public nginx host, not X-Forwarded-Host."""
    conf = (
        pathlib.Path(__file__).resolve().parents[1]
        / "docker"
        / "production"
        / "nginx"
        / "nginx.conf"
    ).read_text()

    for location in ("/api/v1", "/guardian"):
        block = re.search(
            rf"location {re.escape(location)} \{{(?P<body>[\s\S]*?)\n    \}}", conf
        )
        assert block, f"missing {location} proxy location"
        assert 'proxy_set_header X-Forwarded-Host "";' in block.group("body")
