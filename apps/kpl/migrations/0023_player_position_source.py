"""Record where a player's position came from.

Before this, every player the scraper discovered was written as ``MID`` and was
indistinguishable from a midfielder someone had actually verified — all 1132
players in the database were "midfielders". The new column separates the three
cases so the unverified ones can be listed and corrected.

Existing rows are backfilled to ``default`` (the field default), which is the
truth: none of them had ever been checked.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("kpl", "0022_neutral_provider_tags"),
    ]

    operations = [
        migrations.AddField(
            model_name="player",
            name="position_source",
            field=models.CharField(
                choices=[
                    ("default", "Unverified default"),
                    ("provider", "Published by the source"),
                    ("manual", "Set by hand"),
                ],
                default="default",
                max_length=10,
            ),
        ),
        migrations.AddIndex(
            model_name="player",
            index=models.Index(
                fields=["position_source"], name="kpl_player_positio_4a4a15_idx"
            ),
        ),
    ]
