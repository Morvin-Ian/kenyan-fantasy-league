# Production host configuration omits `beheer.fantasykenya.com` in `config/settings/production.py`

## Verdict
defect — the deployment receives requests for `beheer.fantasykenya.com`, but production Django and nginx only configure `fantasykenya.com` and `www.fantasykenya.com`, so the request is rejected before the endpoint runs.

## What happened
A user or upstream service requested the API with `Host: beheer.fantasykenya.com`. Nginx forwarded that host to Django through the API proxy, and Django’s `CommonMiddleware` called `request.get_host()` before URL dispatch. Because the production host allowlist did not contain the hostname, Django raised `DisallowedHost` and the request failed without reaching `config/urls.py`.

## Root cause
The production host contract was incomplete at `config/settings/production.py:45-58`:

```python
SERVED_DOMAINS = [
    "fantasykenya.com",
    "www.fantasykenya.com",
]

ALLOWED_HOSTS = pinned_hosts(ALLOWED_HOSTS, SERVED_DOMAINS)
```

The assumption that the two existing domains were the complete set of production domains does not hold: the live deployment is receiving `beheer.fantasykenya.com`.

Nginx had the same incomplete assumption at `docker/production/nginx/nginx.conf:28-29` and `:43-50`; its application virtual hosts declared only the two existing domains, and the HTTPS guard rejected every other host before the change. Where the request did reach Django, the API locations preserved the incoming host via `proxy_set_header Host $host` at `docker/production/nginx/nginx.conf:79` and `:87`, allowing the unrecognised value to surface as Django’s error.

The traceback’s top frame is in the installed Django dependency (`django.middleware.common.CommonMiddleware`), which is outside this repository and was not independently inspected. The repository code establishes that host validation is intentional; it does not establish whether `beheer.fantasykenya.com` has a valid certificate or whether it should serve this application rather than another service.

## How to reproduce
Send a request to the production API or admin route with:

```http
GET /api/v1/ HTTP/1.1
Host: beheer.fantasykenya.com
```

or:

```http
GET /guardian/ HTTP/1.1
Host: beheer.fantasykenya.com
```

Before the change, nginx forwarded the host when the request entered the application virtual host, and Django rejected it because `beheer.fantasykenya.com` was absent from production `ALLOWED_HOSTS`.

## Blast radius
Requests using `beheer.fantasykenya.com` against Django-proxied `/api/v1` and `/guardian` routes failed before authentication, URL dispatch, or data mutation. Requests using the two previously configured Fantasy Kenya domains were unaffected; arbitrary other hosts remain rejected.

## Likely cause commit
27cbf1f (`feat: serve mogul.manager from the shared nginx edge`) most plausibly exposed the configuration gap: the repository’s shared-edge changes introduced additional hostname routing while the KFL settings and nginx allowlist continued to enumerate only the original two domains. I could not inspect the commit’s file-level diff, so attribution is not conclusive; `cbeff97` has a similar subject and may represent the corresponding merge or follow-up.

## Applied fix
- `config/settings/production.py:45-58` was updated so `SERVED_DOMAINS` and the production fallback allowlist include `beheer.fantasykenya.com`.
- `config/settings/base.py:62-72` was updated so `beheer.fantasykenya.com` is also present in `CSRF_TRUSTED_ORIGINS`.
- `docker/production/nginx/nginx.conf:28-50` was updated to include the hostname in both HTTP and HTTPS `server_name` declarations and in the HTTPS host-validation regular expression, allowing the request to reach the existing API and admin proxy locations.
- `tests/test_allowed_hosts.py:36-38` was extended with a regression assertion that production `ALLOWED_HOSTS` contains `beheer.fantasykenya.com`; the existing nginx assertion was updated to require the hostname in the edge guard.
- Tests were not executed because this environment provides no command-execution access. The nginx configuration must be reloaded or the production stack rebuilt before the running deployment uses these edits.


---

## Error details

```
2026-09-04 06:28:55 [ERROR] django.security.DisallowedHost: Invalid HTTP_HOST header: 'beheer.fantasykenya.com'. You may need to add 'beheer.fantasykenya.com' to ALLOWED_HOSTS.
Traceback (most recent call last):
  File "/usr/local/lib/python3.10/site-packages/django/core/handlers/exception.py", line 55, in inner
    response = get_response(request)
  File "/usr/local/lib/python3.10/site-packages/django/utils/deprecation.py", line 133, in __call__
    response = self.process_request(request)
  File "/usr/local/lib/python3.10/site-packages/django/middleware/common.py", line 48, in process_request
    host = request.get_host()
  File "/usr/local/lib/python3.10/site-packages/django/http/request.py", line 150, in get_host
    raise DisallowedHost(msg)
django.core.exceptions.DisallowedHost: Invalid HTTP_HOST header: 'beheer.fantasykenya.com'. You may need to add 'beheer.fantasykenya.com' to ALLOWED_HOSTS.
```

- Repo: `Morvin-Ian/kenyan-fantasy-league`
- Source: `docker:api`
- First seen: 2026-09-04T03:29:13+00:00
- Fingerprint: `17de27dc35cbfc6f`
