from django.db import migrations, models
import uuid
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("kpl", "0014_rename_is_relagated_team_is_relegated"),
    ]

    operations = [
        migrations.CreateModel(
            name="FixtureLineup",
            fields=[
                ("pkid", models.BigAutoField(primary_key=True, editable=False, serialize=False)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("side", models.CharField(choices=[("home", "Home"), ("away", "Away")], max_length=10)),
                ("formation", models.CharField(blank=True, max_length=20, null=True)),
                ("is_confirmed", models.BooleanField(default=False)),
                ("source", models.CharField(default="manual", max_length=50)),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                ("fixture", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lineups", to="kpl.fixture")),
                ("team", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lineups", to="kpl.team")),
            ],
            options={
                "verbose_name": "Fixture Lineup",
                "verbose_name_plural": "Fixture Lineups",
                "unique_together": {("fixture", "team", "side")},
            },
        ),
        migrations.CreateModel(
            name="FixtureLineupPlayer",
            fields=[
                ("pkid", models.BigAutoField(primary_key=True, editable=False, serialize=False)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("position", models.CharField(blank=True, choices=[("GKP", "Goalkeeper"), ("DEF", "Defender"), ("MID", "Midfielder"), ("FWD", "Forward")], max_length=3, null=True)),
                ("order_index", models.PositiveIntegerField()),
                ("is_bench", models.BooleanField(default=False)),
                ("lineup", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="players", to="kpl.fixturelineup")),
                ("player", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="lineup_entries", to="kpl.player")),
            ],
            options={
                "verbose_name": "Fixture Lineup Player",
                "verbose_name_plural": "Fixture Lineup Players",
                "ordering": ["lineup", "is_bench", "order_index"],
                "unique_together": {("lineup", "order_index")},
            },
        ),
        migrations.CreateModel(
            name="PlayerAlias",
            fields=[
                ("pkid", models.BigAutoField(primary_key=True, editable=False, serialize=False)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("normalized_name", models.CharField(max_length=120)),
                ("jersey_number", models.PositiveIntegerField(blank=True, null=True)),
                ("canonical_player", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="aliases", to="kpl.player")),
                ("team", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="player_aliases", to="kpl.team")),
            ],
            options={
                "verbose_name": "Player Alias",
                "verbose_name_plural": "Player Aliases",
                "unique_together": {("team", "normalized_name")},
            },
        ),
        migrations.AddIndex(
            model_name="playeralias",
            index=models.Index(fields=["team", "normalized_name"], name="kpl_player_alias_team_norm_idx"),
        ),
    ]


