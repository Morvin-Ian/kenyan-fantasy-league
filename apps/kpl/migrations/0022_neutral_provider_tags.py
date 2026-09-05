"""Normalise the provider tags stored on External*Mapping rows.

The tags used to spell out an upstream site's hostname, which put the name of a
third-party source into every row of the database and into any dump or fixture
taken from it. They are now neutral role names matching
``apps.kpl.scraping.providers`` — "primary" for the scheduled-fixture, club and
player ids, "primary:match" for match-report ids.

The old value is discovered from the data rather than written out here, so this
migration names no source either.
"""

from django.db import migrations

PRIMARY = "primary"
PRIMARY_MATCH = "primary:match"
# Tags that are already neutral and must be left alone.
KNOWN = {PRIMARY, PRIMARY_MATCH}
# The old match-report tag was the old primary tag with this suffix.
MATCH_SUFFIX = ":score"

MAPPING_MODELS = (
    "ExternalTeamMapping",
    "ExternalFixtureMapping",
    "ExternalPlayerMapping",
)


def forwards(apps, schema_editor):
    stale = set()
    for model_name in MAPPING_MODELS:
        model = apps.get_model("kpl", model_name)
        stale |= {
            value
            for value in model.objects.values_list("provider", flat=True).distinct()
            if value and value not in KNOWN
        }

    if not stale:
        return

    for model_name in MAPPING_MODELS:
        model = apps.get_model("kpl", model_name)
        for value in stale:
            target = PRIMARY_MATCH if value.endswith(MATCH_SUFFIX) else PRIMARY
            model.objects.filter(provider=value).update(provider=target)

    # Lineups recorded the same tag in `source`. Only rewrite values that were
    # actually written by the scraper — "manual" and the lineup-adapter tags
    # must survive untouched.
    lineup = apps.get_model("kpl", "FixtureLineup")
    for value in stale:
        if value.endswith(MATCH_SUFFIX):
            continue
        lineup.objects.filter(source=value).update(source=PRIMARY)


class Migration(migrations.Migration):

    dependencies = [("kpl", "0021_externalplayermapping")]

    operations = [
        # Irreversible by design: the old tag is discovered from the data, so
        # there is nothing to restore it to. The rows are re-derivable in full
        # by re-running `manage.py sync_kpl`.
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
