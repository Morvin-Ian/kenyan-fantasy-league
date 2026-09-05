"""Service layer for the kpl app.

``lineup_store`` used to live at ``apps/kpl/services.py``. That module was
shadowed by this package the moment it was created, so every
``from apps.kpl.services import upsert_fixture_lineup`` raised ImportError and
the lineup tasks silently failed to register with Celery. It now sits inside the
package and is re-exported here so the historical import path keeps working.

``LineupService`` and ``PlayerService`` are resolved lazily: they reach back into
``apps.kpl.tasks``, which imports this package, so importing them eagerly here
would close a circular import at startup.
"""

from .lineup_store import (
    map_role_to_position,
    match_player_for_team,
    normalize_player_name,
    upsert_fixture_lineup,
)

__all__ = [
    "LineupService",
    "PlayerService",
    "upsert_fixture_lineup",
    "match_player_for_team",
    "map_role_to_position",
    "normalize_player_name",
]

_LAZY = {
    "LineupService": (".lineup", "LineupService"),
    "PlayerService": (".player", "PlayerService"),
}


def __getattr__(name):
    target = _LAZY.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    from importlib import import_module

    module = import_module(target[0], __name__)
    value = getattr(module, target[1])
    globals()[name] = value
    return value


def __dir__():
    return sorted(set(globals()) | set(_LAZY))
