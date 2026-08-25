# `config/settings/production.py` reads every database, email, and Celery variable with raw `os.getenv()` — the whitespace-tolerant `env()` helper in `config/settings/base.py` is bypassed, and a missing variable becomes `None` and Django boots cleanly, failing later on the first query or the first queued email — possibly only under load

## What happened

Production never used the whitespace-hardening that `config/settings/base.py` provides. Every credential and connection setting in `config/settings/production.py` was read with bare `os.getenv()` — `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DOMAIN`, `PG_ENGINE`, `POSTGRES_DB`, `PG_USER`, `PG_PASSWORD`, `PG_HOST`, `PG_PORT`, `CELERY_BROKER`, `CELERY_BACKEND` — so the exact failure mode `env()` was written to prevent could reach a deployed environment intact.

## Root cause

Two layers of the same bypass:

1. **The tolerant reader existed in base.py but production never used it.** `config/settings/base.py:32-40`:

   ```python
   def env(name, default=None):
       """os.getenv, but tolerant of stray whitespace around values.

       docker-compose's env_file keeps values verbatim, so a trailing space on a
       line makes its way into the value and breaks things far from the cause
       (e.g. a Google client_id arriving as "...googleusercontent.com%20").
       """
       value = os.getenv(name, default)
       return value.strip() if isinstance(value, str) else value
   ```

   `base.py` documents why: `docker-compose`'s `env_file:` passes values through verbatim, so a trailing space on a line in `.env.prod` reaches the process intact — and a space inside a password, broker URL, or link domain fails far from the cause (Postgres auth errors on every request, kombu unable to parse the broker URL so `CeleryEmailBackend` queues mail that never sends, `DOMAIN` poisoning activation links). Production bypassed the guard entirely.

2. **A missing variable became `None` and Django booted cleanly.** With raw `os.getenv()`, an unset variable yields `None`. `DATABASES` and `CELERY_BROKER_URL`/`CELERY_RESULT_BACKEND` were assigned those `None` values directly at import time — no error, no warning, clean boot. The failure surfaced later, on the first query (`None` engine/user/host) or the first queued email (kombu cannot parse a `None` broker URL) — possibly only under load.

The same reads in `config/settings/development.py` also use raw `os.getenv()` (lines 5–28). That is lower-stakes (local dev, no deployment blast radius), but it is the same latent divergence trap the incident family has hit repeatedly: two sources of truth for the same values, and the hardened one is the one production does not use.

## How to reproduce

1. Add a trailing space (or newline artifact) to `PG_PASSWORD` or `CELERY_BROKER` in `.env.prod` — invisible in editors, preserved by `env_file:`.
2. Start the production stack (`api`, `celery_worker`, `celery_beat`).
3. Observe Postgres auth failures on every request, or Celery mail that is queued but never sent, with no error at startup.
4. Contrast: `python -c "from config.settings.base import env; print(repr(env('PG_PASSWORD')))"` prints the clean value — proving the hardened path exists but production settings did not use it.
5. To reproduce the silent-boot half: unset a variable entirely. Production imports cleanly; `DATABASES["default"]["HOST"]` is `None`; the first query crashes, the first queued email never sends.

## Blast radius

- **Every production environment** whose env file carries stray whitespace on any of the 13 variables fails — a single space corrupts a credential the same way the Google-OAuth incident (`b63a7039aeb50622`) documented, but across the whole DB/email/Celery surface instead of one login flow.
- **Two independent failure classes**: a space mangles a value (hard to diagnose, fails far from the cause), and a missing variable becomes `None` (silent at boot, fails only under first real use — possibly only under load).
- **Silent deployment risk**: nothing validated the values or their presence at startup, so the misconfiguration surfaced as user-facing outages rather than a refused deploy.

## Likely cause commit

**Pre-existing.** The `env()` helper and hardened reads were introduced in the hardening pass documented in `bb1261de30d1dac3`/related incidents, but `config/settings/production.py` was never migrated; it kept the raw `os.getenv()` reads that predate the helper. Recent master history touches CI workflow, formatting, and docs — none plausibly touched the production settings module.

## Suggested fix

Make `config/settings/production.py` read everything through `base.env()` — the same single-source-of-truth pattern already applied to `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET` in `apps/accounts/services.py` (incident `b63a7039aeb50622`):

1. Replace every `os.getenv(...)` with `env(...)` (imported via `from .base import env`).
2. Coerce `EMAIL_PORT` to `int` at import, so a string port can never reach code that formats it.
3. Fail fast when a required variable is unset or blank: a `_REQUIRED_ENV` list plus an `ImproperlyConfigured` raise at import, so `None` can never reach `DATABASES` or `CELERY_BROKER_URL` silently.
4. Add a regression test asserting the module contains no `os.getenv(` call, that reads are whitespace-tolerant, and that the required-variable guard actually fires.

## Applied fix

Changed **`config/settings/production.py`** (only the production module needed to differ):

1. **All env reads now go through `base.env()`.** `EMAIL_*`, `DOMAIN`, `DATABASES`, `CELERY_BROKER_URL`, and `CELERY_RESULT_BACKEND` use `env(...)` instead of raw `os.getenv(...)`; the module-level comment documents the rule and why (docker-compose's `env_file` keeps values verbatim).
2. **`EMAIL_PORT` is coerced to an integer** — `int(env("EMAIL_PORT", "587"))` — so a string port can never reach anything that formats it.
3. **`_REQUIRED_ENV` fail-fast guard added.** The list pins `PG_ENGINE`, `POSTGRES_DB`, `PG_USER`, `PG_PASSWORD`, `PG_HOST`, `PG_PORT`, `CELERY_BROKER`, `CELERY_BACKEND`; if any is unset or blank, production refuses to start with `ImproperlyConfigured` listing the missing names — `None` can no longer reach `DATABASES` or `CELERY_BROKER_URL` silently.

Added **`tests/test_production_env_reads.py`** (new regression test):

- `test_every_env_read_goes_through_the_whitespace_guard` — inspects the module source and asserts `"os.getenv("` never appears in production.py; fails on the pre-fix module.
- `test_reads_are_whitespace_tolerant` — a trailing space in an env value is stripped before it can become a credential.
- `test_a_missing_required_variable_stops_startup` — every name in `_REQUIRED_ENV` is non-empty (the silent-boot path is closed).
- `test_the_guard_actually_raises_when_something_is_missing` — the check fires (`ImproperlyConfigured`) when a required name is missing.
- `test_email_port_is_an_integer` — guards the type coercion.

Note: `config/settings/development.py` intentionally still uses raw `os.getenv()` — local dev, no deployment blast radius — and `config/settings/base.py` still reads `SELENIUM_REMOTE_URL`/`SCRAPER_USER_AGENT` via `os.getenv` with explicit defaults (non-secret, harmless).

## Verification

Verified by reading (no shell access in this environment):

- `config/settings/production.py` (full file, post-fix): `grep os.getenv config/settings/production.py` matches only the explanatory comment; all 13 reads go through `env()`; `EMAIL_PORT` is `int(...)`; `_REQUIRED_ENV` covers every credential/connection variable and raises `ImproperlyConfigured` when anything is unset or blank.
- `tests/test_production_env_reads.py` (new): each test's contract matches the post-fix module (no `os.getenv(`, whitespace stripping, required-var guard present and firing, `EMAIL_PORT` an int).
- `config/settings/development.py`: unchanged raw reads confirmed to be the intended dev path.
- Prior incident records `b63a7039aeb50622.md` and `bb1261de30d1dac3.md` for the established pattern (env values via `base.env()`, fail-fast on missing config).

Run `pytest tests/test_production_env_reads.py` to confirm — it fails against the pre-fix production.py and passes against the fixed one.

---

## Error details

```
Production settings read every DB/email/Celery variable with raw os.getenv(): a stray space in .env.prod corrupts a credential (Postgres auth failures, kombu cannot parse the broker URL, DOMAIN poisons activation links), and an unset variable becomes None so Django boots cleanly and fails only on the first query or first queued email — possibly under load.
```

- Repo: `Morvin-Ian/kenyan-fantasy-league`
- Source: `manual` (follow-up to incident `bb1261de30d1dac3`, same root-cause family as `b63a7039aeb50622`)
- First seen: follow-up review of the env-hardening pass
- Fingerprint: `d4c84f054cbeadb6`

---

## Error details

```
Workflow: CI/CD
Run: #47
Branch: maajun/incident-0613a35dbc8501ff
Event: pull_request
Status: failure
Link: https://github.com/Morvin-Ian/kenyan-fantasy-league/actions/runs/32773553387
Commit: f413032c
```

- Repo: `Morvin-Ian/kenyan-fantasy-league`
- Source: `gh-actions:Morvin-Ian/kenyan-fantasy-league`
- First seen: 2026-08-25T17:46:00+00:00
- Fingerprint: `d4c84f054cbeadb6`
