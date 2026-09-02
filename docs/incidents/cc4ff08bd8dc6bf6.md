# TLS default server in `docker/production/nginx/nginx.conf` accepted unknown SNI before rejecting the Host header

## Verdict
defect — an unserved hostname was able to complete TLS handling at the shared nginx edge and reach Django when the Host-header guard was bypassed or unavailable, producing avoidable application error traces.

## What happened
A request carrying `Host: kanri.fantasykenya.com` reached Django, where `CommonMiddleware` called `request.get_host()` and Django rejected the hostname with `DisallowedHost`. The user or scanner received Django’s host-validation failure rather than an edge rejection, while the application logged a traceback. The supplied production log could not be opened because it is outside the permitted workspace, so the timestamp and request path cannot be independently verified.

## Root cause
The TLS default virtual host in `docker/production/nginx/nginx.conf:14-24` previously completed the TLS handshake using the primary site certificate before returning `444`:

```nginx
server {
    listen 443 ssl default_server;
    http2 on;
    server_name _;
    ...
    return 444;
}
```

It assumed that returning `444` after TLS setup was sufficient to prevent unknown TLS hostnames from progressing toward the application. That assumption does not hold where the effective edge configuration is stale, overridden, or traffic reaches the named TLS virtual host using a recognised SNI value but an unrecognised HTTP `Host` value. The named application server does reject an unrecognised HTTP host at `docker/production/nginx/nginx.conf:47-51`:

```nginx
if ($host !~ ^(fantasykenya\.com|www\.fantasykenya\.com)$) {
    return 444;
}
```

Django’s refusal is correct: `config/settings/production.py:45-54` permits only `fantasykenya.com` and `www.fantasykenya.com`; `kanri.fantasykenya.com` is not declared as served anywhere in the repository.

## How to reproduce
Send a TLS request to the public nginx address with SNI `kanri.fantasykenya.com` and a request target such as `/api/v1`, or send a request using recognised SNI and `Host: kanri.fantasykenya.com`. Before the change, the default TLS server accepted the handshake; if the HTTP-host rejection was not active, the proxy locations preserve `$host` at `docker/production/nginx/nginx.conf:75-80`, allowing Django to raise `DisallowedHost`.

## Blast radius
Any unknown TLS server name or HTTP Host header can trigger the same Django error if it reaches the API proxy, including automated Host-header probes. The same proxy pattern exists for `/guardian` at `docker/production/nginx/nginx.conf:83-89`; valid primary-domain traffic is unchanged.

## Likely cause commit
27cbf1f (`feat: serve mogul.manager from the shared nginx edge`) most plausibly introduced the shared-edge/default-host exposure: `docker/production/nginx/mogul.conf:9-11` explicitly relies on `fantasykenya.com` remaining the unmatched-host default. Later nginx hardening commits added the current HTTP-level `444` guards, but the live error indicates the edge still accepted traffic that should have been rejected.

## Applied fix
- `docker/production/nginx/nginx.conf:21-24` now sets `ssl_reject_handshake on;` in the HTTPS `default_server`, so nginx rejects unknown SNI during TLS negotiation rather than serving the primary-site certificate and proceeding to HTTP handling.
- `tests/test_allowed_hosts.py:68-71` now requires the default HTTPS server to retain `ssl_reject_handshake on;` before its `444` response.

Verify by rebuilding or deploying the nginx service from `docker-compose.prod.yml`, then requesting the edge with SNI `kanri.fantasykenya.com`: nginx should reject the TLS handshake and Django should receive no request or emit no `DisallowedHost` record. Also request `/api/v1` with recognised `fantasykenya.com` SNI and `Host: kanri.fantasykenya.com`; the existing HTTP-host guard should return `444`. I could not run tests, reload nginx, or inspect the live container because this environment has no command-execution access and the production host is outside the workspace.


---

## Error details

```
2026-09-02 17:40:48 [ERROR] django.security.DisallowedHost.response_for_exception:124 - Invalid HTTP_HOST header: 'kanri.fantasykenya.com'. You may need to add 'kanri.fantasykenya.com' to ALLOWED_HOSTS.
Traceback (most recent call last):
  File "/usr/local/lib/python3.10/site-packages/django/core/handlers/exception.py", line 55, in inner
    response = get_response(request)
  File "/usr/local/lib/python3.10/site-packages/django/utils/deprecation.py", line 133, in __call__
    response = self.process_request(request)
  File "/usr/local/lib/python3.10/site-packages/django/middleware/common.py", line 48, in process_request
    host = request.get_host()
  File "/usr/local/lib/python3.10/site-packages/django/http/request.py", line 150, in get_host
    raise DisallowedHost(msg)
django.core.exceptions.DisallowedHost: Invalid HTTP_HOST header: 'kanri.fantasykenya.com'. You may need to add 'kanri.fantasykenya.com' to ALLOWED_HOSTS.
```

- Repo: `Morvin-Ian/kenyan-fantasy-league`
- Source: `logfile:/root/kenyan-fantasy-league/logs/fantasy_league.log`
- First seen: 2026-09-02T14:41:05+00:00
- Fingerprint: `cc4ff08bd8dc6bf6`
