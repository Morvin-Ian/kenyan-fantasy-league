# `events.fantasykenya.com` DisallowedHost is the host pin working as designed — no code change

## Summary

Production logged `django.security.DisallowedHost: Invalid HTTP_HOST header: 'events.fantasykenya.com'`
(`docker:api`, first seen 2026-08-24T19:46:22Z). Investigation confirms this is the
intended behavior of the pin introduced in `994136b`, not a regression:
`config/settings/production.py:45` serves exactly the two domains nginx has
`server_name` blocks for, and `events.fantasykenya.com` is referenced nowhere in
the repository — no route, no client view, no cert path, no env var. Django
refused the Host header and returned 400; nothing else was affected. Filing this
so the next `*.fantasykenya.com` DisallowedHost line is triaged as expected
noise rather than an outage.

## What happened

A request reached gunicorn with `Host: events.fantasykenya.com`. nginx has no
matching vhost (`docker/production/nginx/nginx.conf:8,24` list only
`fantasykenya.com` and `www.fantasykenya.com`), so its default server proxied
the request to the API preserving the original Host
(`proxy_set_header Host $host;`, nginx.conf:52). `CommonMiddleware` called
`request.get_host()` (`django/middleware/common.py:48`), which raised
`DisallowedHost`; Django converted it to a 400 response and logged the ERROR
line. The requester saw 400 Bad Request.

## Why this is by design

- `config/settings/production.py:45,54` pins production to
  `SERVED_DOMAINS = ["fantasykenya.com", "www.fantasykenya.com"]`, falling back
  to that list whenever `.env.prod` leaves `ALLOWED_HOSTS` unset or blank. The
  pin was introduced by `994136b` precisely so arbitrary Host headers are
  refused behind `SECURE_HSTS_PRELOAD` and `USE_X_FORWARDED_HOST`
  (production.py:61,68-70).
- The refusal cannot be a routing accident: `tests/test_allowed_hosts.py:36-52`
  asserts `SERVED_DOMAINS` equals the `server_name` entries parsed out of
  `nginx.conf`, so settings and proxy cannot drift silently.
- There is no TLS path to the hostname anyway: the certblock is
  `/etc/letsencrypt/live/fantasykenya.com/` (nginx.conf:29-30), which does not
  cover `events.fantasykenya.com`, so browsers cannot complete the handshake
  without clicking through a warning. Traffic arriving with this Host is
  almost certainly scanners or such click-through clients.
- Precedent: the identical signature fired for `account.fantasykenya.com` on
  2026-08-23 (`docs/incidents/47fa8ad55a8e4253.md:101`) — stray subdomain Host
  headers reaching the default vhost is a recurring, expected pattern.

## What would have to change to serve it

If the product decision is made that `events.fantasykenya.com` should exist,
three coordinated edits are required — adding it to `ALLOWED_HOSTS` alone would
accept a host nginx/TLS cannot serve:

1. `config/settings/production.py:45` — append it to `SERVED_DOMAINS`.
2. `docker/production/nginx/nginx.conf:8,24` — add it to both `server_name`
   directives.
3. Obtain a certificate covering it (extend the existing certbot webroot
   renewal, nginx.conf:11-13, docker-compose.prod.yml:103-115) and reference it
   in the TLS server block.

Until then, no file in this repository should differ.

## Verification

Read-only analysis (no shell access): `config/settings/base.py:58-71`,
`config/settings/production.py` (full file), `docker/production/nginx/nginx.conf`
(full file), `docker-compose.prod.yml`, `client/vite.config.ts:13-16`,
`tests/test_allowed_hosts.py`, `config/urls.py`, and prior incidents
`47fa8ad55a8e4253.md` and `bb1261de30d1dac3.md`. Gap: the gitignored server-side
`.env.prod` and live DNS were not inspectable; if it set
`ALLOWED_HOSTS=events.fantasykenya.com …` the env path would refuse it too, and
the pin at `production.py:54` produces the identical rejection either way, so
the diagnosis does not depend on it.

---

## Error details

```
2026-08-24 22:46:06 [ERROR] django.security.DisallowedHost: Invalid HTTP_HOST header: 'events.fantasykenya.com'. You may need to add 'events.fantasykenya.com' to ALLOWED_HOSTS.
Traceback (most recent call last):
  File "/usr/local/lib/python3.10/site-packages/django/core/handlers/exception.py", line 55, in inner
    response = get_response(request)
  File "/usr/local/lib/python3.10/site-packages/django/utils/deprecation.py", line 133, in __call__
    response = self.process_request(request)
  File "/usr/local/lib/python3.10/site-packages/django/middleware/common.py", line 48, in process_request
    host = request.get_host()
  File "/usr/local/lib/python3.10/site-packages/django/http/request.py", line 150, in get_host
    raise DisallowedHost(msg)
django.core.exceptions.DisallowedHost: Invalid HTTP_HOST header: 'events.fantasykenya.com'. You may need to add 'events.fantasykenya.com' to ALLOWED_HOSTS.
```

- Repo: `Morvin-Ian/kenyan-fantasy-league`
- Source: `docker:api`
- First seen: 2026-08-24T19:46:22+00:00
- Fingerprint: `d4c84f054cbeadb6`
