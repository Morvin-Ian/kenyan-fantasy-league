"""Regression test: the production domains stay in ALLOWED_HOSTS even when the
deploy pins the variable to a value that omits them.

nginx forwards the real Host header (``proxy_set_header Host $host`` in
``docker/production/nginx/nginx.conf``), so Django must always accept
``fantasykenya.com`` regardless of what the server's gitignored ``.env.prod``
puts in ALLOWED_HOSTS. Without this, a pinned ALLOWED_HOSTS that forgets the
domain makes every proxied request fail with ``DisallowedHost``.
"""

import importlib

from config.settings import base


def test_allowed_hosts_always_accept_production_domains(monkeypatch):
    # The production deploy pins hosts; the value in .env.prod must not be
    # able to lock out the public domain.
    with monkeypatch.context() as mp:
        mp.setenv("ALLOWED_HOSTS", "localhost api nginx")
        importlib.reload(base)

        assert "fantasykenya.com" in base.ALLOWED_HOSTS
        assert "www.fantasykenya.com" in base.ALLOWED_HOSTS

    # Leave the module matching the real environment for other tests.
    importlib.reload(base)
