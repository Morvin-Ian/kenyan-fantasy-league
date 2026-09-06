# KPL data pipeline

Everything the app knows about the league — clubs, badges, squads, the calendar,
the table, results, scorers, match reports — comes from the tasks in
`apps/kpl/tasks/sync.py`.

## No source is named in this repository

Hostnames, page paths and the competition label all live in the gitignored
`.env` / `.env.prod`. `.env.example` carries the placeholders and explains each
one. `tests/test_scraping_infrastructure.py` fails the build if a configured
hostname ever appears under `apps/`.

| Variable | What it is |
| --- | --- |
| `SCRAPER_PRIMARY_BASE_URL` | primary source root |
| `SCRAPER_PRIMARY_COMPETITION` | competition label, minus the season |
| `SCRAPER_PRIMARY_PATHS` | `role=path` pairs for the nine pages used |
| `SCRAPER_PROVIDER_HOSTS` | `provider=host` pairs for the lineup adapters |
| `SCRAPER_LINEUP_PROVIDERS` | which lineup adapters to try, in order |

## Layout

```
apps/kpl/scraping/
  http.py                  timeouts, backoff, per-host throttle, conditional GET
  locks.py                 Redis locks so beat runs cannot overlap
  normalize.py             club/player name matching across sources
  exceptions.py            transient vs. structural failure
  providers/primary.py     source of record — parses nine pages
apps/kpl/tasks/
  base.py                  retry, timeout and locking policy for every sync task
  sync.py                  the tasks themselves
```

## Design rules

**Discover, never hard-code.** The competition id changes every season. It is
looked up from the source's own index and cached for 12 hours, so a season
rollover needs no redeploy. The old scorers task pinned one id and quietly kept
re-reading a finished season.

**Parse everything before writing anything.** The old standings task deleted the
table and *then* fetched, so any failure left the site with no table. Now the
whole snapshot is built and every row matched to a club before a single delete.

**Key on the source's ids.** Clubs, players, fixtures and match reports all carry
stable ids, stored in `External*Mapping`. Re-running any sync is a no-op, and a
club renaming itself does not create a duplicate.

**Fail loudly on structure, quietly on absence.** A moved column raises
`StructureChanged`. An empty league table in August is reported as "not
published yet", because it genuinely is.

## Running it

```bash
python manage.py sync_kpl                      # full pipeline, dependency order
python manage.py sync_kpl --step teams --step fixtures
python manage.py sync_kpl --season             # report the season discovered
python manage.py sync_kpl --list
```

`sync_kpl` runs the seven scheduled steps by default; `--step match-details`
settles finished matches and is opt-in.

Beat runs the same tasks on the schedule in `config/settings/base.py`
(`CELERY_BEAT_SCHEDULE`), written in Kenyan local time.

## Worker stability

* Each task holds a Redis lock; a run that finds it held exits instead of
  stacking a second scrape onto the same host.
* Only `SourceUnavailable` retries, with exponential backoff and jitter. A
  `ParseError` fails immediately — retrying re-downloads the same broken page.
* `acks_late` + `reject_on_worker_lost`: a redeploy or OOM redelivers the job.
* Soft and hard time limits stop a stalled scrape holding a worker slot.
* `--max-tasks-per-child` recycles processes so lxml/Chrome memory stays flat.
* Requests are throttled per host and use conditional GETs, so an unchanged page
  costs a 304.

### The scraping queue

`docker/production/django/celery/worker/start-scraping` runs a **second** worker
that consumes only the `scraping` queue, while the existing worker keeps serving
`celery` (emails, fantasy points — anything a user waits on).

Without it both share one pool: the fixtures page alone takes ~17s, and a source
that hangs holds its slot until the time limit. With four slots, a handful of
scrapes can leave nothing for user-facing work. Splitting them means a wedged
scrape degrades data freshness and nothing else, and lets scraping run at
concurrency 2 (polite to a small host) while user work stays at 4.

It is **opt-in**. `CELERY_SCRAPING_QUEUE_ENABLED=false` leaves
`CELERY_TASK_ROUTES` empty, so every task stays on the default queue and the
current single worker keeps working unchanged. To adopt it:

1. rebuild the images (the start scripts are baked in, not mounted);
2. bring up the `celery_scraping_worker` service;
3. set `CELERY_SCRAPING_QUEUE_ENABLED=true` and restart.

If you would rather not run a second container, delete the
`celery_scraping_worker` service and leave the flag off — nothing else depends
on it.

## What the sources do and do not give us

* Match reports carry goals with minutes, cards with minutes, and both full
  lineups — enough to settle a gameweek. They are published **after** the final
  whistle, so this is settlement, not live scoring.
* Substitutions are not published as events; the bench is a list, so exact
  minutes played cannot be derived.
* Ages are not published anywhere.
* **Positions are published, but only on a club's own roster page**
  (`squad` role), never on the combined squads page the importer used to read
  alone. That is why every player in the database was a midfielder: the page
  being read has no position column at all, so `sync_players` wrote the `MID`
  placeholder for all of them.

  `sync_players` now reads both — the combined page for who is registered, the
  club page for position and shirt number. Note two things about the club page:

  * It carries **one table per competition** the club is entered in (league,
    domestic cups, friendlies). The table is selected by the current season's
    competition id; taking the first one on the page reads a cup squad.
  * The source opens a new season's competition before clubs register squads
    for it, so for the first weeks of a season that table is empty. The parser
    then falls back to the club's most recent published roster, preferring this
    competition's own past seasons over a cup — a position is a property of the
    player, not of the season.

* Coverage is partial: the source leaves the position blank for a little under
  half the league. Those players keep the `MID` placeholder, because the fantasy
  scoring rules branch on a position and cannot take a blank — but they are
  tagged `position_source="default"`, which is what makes them findable:

  | `position_source` | meaning | overwritten by `sync_players`? |
  | --- | --- | --- |
  | `default` | nobody has ever verified this; it is the `MID` placeholder | yes |
  | `provider` | the source published it | yes |
  | `manual` | set by hand (admin, CSV upload, or API) | **never** |

  Filter Players on "Unverified default" in the admin to get exactly the list
  that still needs a human. The admin action *Confirm position* flips a row to
  `manual` so the nightly sync stops touching it.

## Live scoring

`apps/kpl/tasks/live_games.py` is a separate, older path: it drives a browser
against `MATCHES_URL` for in-play scores. It is untouched by this pipeline and
still the only source of live updates, because the match report `sync_match_details`
reads is published after the final whistle. The two do not overlap —
`MatchEventService` deduplicates on `event_key`, so whichever arrives first wins
and the other is a no-op.
