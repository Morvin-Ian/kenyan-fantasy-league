"""Regression test: docker entrypoints must not shell-interpolate DB credentials.

The api/worker/beat images all run the same entrypoint, which waits for
Postgres with a small Python snippet. When that snippet was built with an
unquoted heredoc (``python3 << END``), bash expanded ``${PG_PASSWORD}`` and the
other ``PG_*`` variables *before* Python saw them, so any password containing
``$``, a backtick, ``\\`` or a quote was silently corrupted and postgres
answered ``FATAL: password authentication failed for user "postgres"``. The
snippet must receive the values through the environment and the heredoc must be
quoted.
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
ENTRYPOINTS = [
    REPO_ROOT / "docker" / "local" / "django" / "entrypoint",
    REPO_ROOT / "docker" / "production" / "django" / "entrypoint",
]

INTERPOLATED = (
    "${POSTGRES_DB}",
    "${PG_USER}",
    "${PG_PASSWORD}",
    "${PG_HOST}",
    "${PG_PORT}",
)


@pytest.mark.parametrize(
    "entrypoint",
    ENTRYPOINTS,
    ids=lambda path: path.parent.parent.name,
)
def test_postgres_ready_passes_credentials_via_environment(entrypoint):
    body = entrypoint.read_text()

    # Quoted delimiter: bash must not expand anything inside the heredoc.
    assert "<<'END'" in body, "postgres_ready() must use a quoted heredoc"

    # The Python snippet reads the values itself instead of inheriting
    # shell-expanded text.
    assert 'os.environ["POSTGRES_DB"]' in body
    assert 'os.environ["PG_USER"]' in body
    assert 'os.environ["PG_PASSWORD"]' in body
    assert 'os.environ["PG_HOST"]' in body
    assert 'os.environ["PG_PORT"]' in body

    # The command prefix deliberately uses shell expansion to pass the already
    # validated values into Python's environment. Only the quoted heredoc must
    # remain free of shell interpolation.
    heredoc = body.split("<<'END'", maxsplit=1)[1].split("\nEND", maxsplit=1)[0]
    for var in INTERPOLATED:
        assert var not in heredoc
