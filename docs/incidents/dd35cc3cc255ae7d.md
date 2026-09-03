# Production nginx reload cadence delays `docker/production/nginx/nginx.conf` host rejection for up to six hours

## Verdict
defect — the checked-in nginx guard rejects unknown hosts, but `docker-compose.prod.yml` reloads mounted edge configuration only every six hours, allowing a live deployment to continue forwarding invalid hosts to Django after the fix is deployed.

## What happened
A client sent `Host: area-riservata.fantasykenya.com` to the public deployment. Django rejected it in `CommonMiddleware` because production allows only `fantasykenya.com` and `www.fantasykenya.com` (`config/settings/production.py:45-54`), before any view or data mutation ran. Although the repository’s nginx configuration now rejects this host at the edge, the running deployment still had a configuration state that forwarded it to Django.

## Root cause
`docker-compose.prod.yml:66-67` mounted `docker/production/nginx/nginx.conf` into the running nginx container but scheduled reloads only every six hours:

```yaml
# Reload every 6h so renewed certs get picked up without a manual restart.
command: /bin/sh -c 'while :; do sleep 6h & wait $${!}; nginx -s reload; done & nginx -g "daemon off;"'
```

The nginx configuration already rejects unknown TLS hosts before proxying at `docker/production/nginx/nginx.conf:14-24` and `:47-51`:

```nginx
server_name _;
...
return 444;
```

```nginx
if ($host !~ ^(fantasykenya\.com|www\.fantasykenya\.com)$) {
    return 444;
}
```

The failed assumption was that mounting a changed nginx configuration makes the running nginx process apply it promptly. Nginx retains its loaded configuration until a reload, so the six-hour interval leaves a long window in which a deployed host-rejection fix is present on disk but inactive.

## How to reproduce
Deploy the repository with a running nginx container that loaded an older configuration without the unknown-host guard, then update the mounted `docker/production/nginx/nginx.conf`. Before the next scheduled reload, send:

```http
GET /api/v1/ HTTP/1.1
Host: area-riservata.fantasykenya.com
```

The stale nginx worker can forward the request through `/api/v1` (`docker/production/nginx/nginx.conf:75-80`), after which Django rejects it against `config/settings/production.py:45-54`.

## Blast radius
Any nginx configuration change mounted through `docker-compose.prod.yml:54`, including the unknown-host rejection, can remain inactive for nearly six hours. During that window, arbitrary hosts sent to `/api/v1` or `/guardian` can continue to produce Django `DisallowedHost` errors because those locations proxy `$host` at `docker/production/nginx/nginx.conf:75-89`.

## Likely cause commit
27cbf1f (`feat: serve mogul.manager from the shared nginx edge`) most plausibly introduced the original unsafe unmatched-host routing: `docker/production/nginx/mogul.conf:9-11` documents that the KFL server remains the default for unmatched hostnames. The current source guard exists, but the six-hour reload cadence in `docker-compose.prod.yml:66-67` delayed its effective application.

## Applied fix
- `docker-compose.prod.yml:66-68` now reloads nginx every five minutes rather than every six hours, so mounted edge-configuration changes—including the existing unknown-host `444` guards—become active promptly while certificate renewal continues to work without manual intervention.
- `tests/test_allowed_hosts.py:118-128` now asserts that the production compose configuration reloads nginx and no longer contains the six-hour sleep interval.

Verify by running the repository test suite including `tests/test_allowed_hosts.py`, deploying the compose change, and checking the nginx container after at most five minutes. A request to `/api/v1/` with `Host: area-riservata.fantasykenya.com` should be closed with nginx status `444`, with no corresponding `django.security.DisallowedHost` log entry. I could not run tests or inspect/reload the production container because command execution and server files outside the workspace are unavailable.


---

## Error details

```
2026-09-03 06:17:35 [ERROR] django.security.DisallowedHost.response_for_exception:124 - Invalid HTTP_HOST header: 'area-riservata.fantasykenya.com'. You may need to add 'area-riservata.fantasykenya.com' to ALLOWED_HOSTS.
Traceback (most recent call last):
  File "/usr/local/lib/python3.10/site-packages/django/core/handlers/exception.py", line 55, in inner
    response = get_response(request)
  File "/usr/local/lib/python3.10/site-packages/django/utils/deprecation.py", line 133, in __call__
    response = self.process_request(request)
  File "/usr/local/lib/python3.10/site-packages/django/middleware/common.py", line 48, in process_request
    host = request.get_host()
  File "/usr/local/lib/python3.10/site-packages/django/http/request.py", line 150, in get_host
    raise DisallowedHost(msg)
django.core.exceptions.DisallowedHost: Invalid HTTP_HOST header: 'area-riservata.fantasykenya.com'. You may need to add 'area-riservata.fantasykenya.com' to ALLOWED_HOSTS.
```

- Repo: `Morvin-Ian/kenyan-fantasy-league`
- Source: `logfile:/root/kenyan-fantasy-league/logs/fantasy_league.log`
- First seen: 2026-09-03T03:17:49+00:00
- Fingerprint: `dd35cc3cc255ae7d`
