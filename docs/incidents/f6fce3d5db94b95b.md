# Production deployment review: Celery runs on development settings, and dev tooling (`watchmedo`, `runserver`) is baked into the production images

## What happened

A review of the production deployment path (`docker-compose.prod.yml`, the `docker/production/django/*` scripts, and `config/celery.py`) found three concrete, verifiable defects. None of them has produced an outage yet — the two settings modules are currently identical, which masks #1 — but each is wrong wiring that breaks silently the moment anything diverges:

1. **The production Celery worker and beat containers load the *development* settings module, unconditionally.**
2. **The production Celery worker/beat/flower start scripts run under `watchmedo auto-restart`** — a dev hot-reload file-watcher (`watchdog==5.0.2`, `requirements.txt:71`) that spawns Celery as a child instead of `exec`-ing it.
3. **The production `api` container serves traffic with Django's dev server `runserver`** instead of a WSGI server.

## Root cause

### 1. Celery ignores `DJANGO_SETTINGS_MODULE` and always loads `config.settings.development`

`config/celery.py:8-11`:

```python
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("config")
app.config_from_object("config.settings.development", namespace="CELERY")
```

The second line is decisive: `config_from_object("config.settings.development", ...)` is unconditional, so even if `.env.prod` sets `DJANGO_SETTINGS_MODULE=config.settings.production`, the Celery app object still reads `CELERY_*` from the development module. The production compose (`docker-compose.prod.yml:60-90`) gives `celery_worker` and `celery_beat` the production image with `env_file: .env.prod`, yet their settings come from the dev module name. Today `config/settings/development.py` and `config/settings/production.py` are byte-identical (same `DATABASES` env reads at lines 15-24, same `CELERY_BROKER_URL`/`CELERY_RESULT_BACKEND` at 27-29), which is why nothing has failed yet — the bug is a latent divergence trap: any future edit that makes production.py differ (broker URL, task routing, timezone, logging, email, cache) will apply only to the `api` container and never to background tasks, and `beat` will keep scheduling on dev settings. The same `setdefault("config.settings.development")` pattern also appears in `manage.py:9` and `config/wsgi.py:14` (those are `setdefault`, so an env var would win there — but nothing in `docker/production/django/start` sets the module, so whether prod `api` runs dev or prod settings depends entirely on the gitignored `.env.prod`).

### 2. Production Celery is started by a file-watcher dev tool

`docker/production/django/celery/worker/start:5` and `docker/production/django/celery/beat/start:9-12` are byte-identical to the `docker/local/django/celery/*` versions:

```bash
watchmedo auto-restart -d config/ -p "*.py" -- celery -A config worker --loglevel=info
```

`watchmedo` (from `watchdog==5.0.2`) watches `config/` and restarts Celery whenever a `.py` file changes — a convenience for local hot-reload, wrong in a production container that never edits its own source. Two concrete harms:

- **Signal handling.** `watchmedo` spawns Celery as a child process and does not reliably forward signals. `docker compose down`, container restarts, and deploys send SIGTERM to the wrapper; Celery may be killed without the graceful-shutdown window, dropping in-flight tasks mid-run.
- **Deploy races.** The CI deploy runs `git pull --ff-only origin master` (`ci.yml:118`), which rewrites `config/*.py` while `watchmedo` is watching them — the worker/beat hot-restart in the middle of a deploy, racing the migrate step (`ci.yml:125-137`).

The prod flower script has the same pattern (`docker/production/django/celery/flower/start:6-7`), though flower is not in the prod compose.

### 3. Production API runs `runserver`

`docker/production/django/start:10-12`:

```bash
python3 manage.py migrate --no-input
python3 manage.py collectstatic --no-input
python3 manage.py runserver 0.0.0.0:8000
```

Django's `runserver` is

---

## Error details

```
2026-08-22 21:54:21.421 UTC [181] FATAL:  password authentication failed for user "wog"
```

- Repo: `Morvin-Ian/kenyan-fantasy-league`
- Source: `docker:postgres-db`
- First seen: 2026-08-22T21:56:46+00:00
- Fingerprint: `f6fce3d5db94b95b`
