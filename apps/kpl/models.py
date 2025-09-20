# pyright: reportMissingImports=false, reportMissingTypeStubs=false, reportAttributeAccessFromUnknown=false
# pyright: reportMissingImports=false, reportMissingTypeStubs=false
# pyright: reportMissingTypeStubs=false, reportMissingImports=false, reportGeneralTypeIssues=false
from django.db import models

from util.models import TimeStampedUUIDModel

FIXTURE_STATUS = [
    ("upcoming", "Upcoming"),
    ("live", "Live"),
    ("postponed", "Postponed"),
    ("completed", "Completed"),
]

POSITION_CHOICES = [
    ("GKP", "Goalkeeper"),
    ("DEF", "Defender"),
    ("MID", "Midfielder"),
    ("FWD", "Forward"),
]


class Team(TimeStampedUUIDModel):
    name = models.CharField(max_length=100)
    logo_url = models.URLField()
    jersey_image = models.ImageField(upload_to="team_jerseys/", null=True, blank=True)
    is_relegated = models.BooleanField(
        default=False,
        help_text="Indicates if the team has been relegated from the league",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Team"
        verbose_name_plural = "Teams"

    def __str__(self) -> str:
        return self.name


class Player(TimeStampedUUIDModel):
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players")
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    jersey_number = models.PositiveIntegerField(null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    current_value = models.DecimalField(max_digits=6, decimal_places=2, default=4.00)

    class Meta:
        ordering = ["team"]
        verbose_name = "Player"
        verbose_name_plural = "Players"

    def __str__(self) -> str:
        return f"{self.name} ({self.team.name}) - {self.get_position_display()}"  # type: ignore[attr-defined]


class Standing(TimeStampedUUIDModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="standings")
    position = models.PositiveIntegerField()
    played = models.PositiveIntegerField()
    wins = models.PositiveIntegerField()
    draws = models.PositiveIntegerField()
    losses = models.PositiveIntegerField()
    goals_for = models.PositiveIntegerField()
    goals_against = models.PositiveIntegerField()
    goal_differential = models.IntegerField()
    points = models.PositiveIntegerField()
    period = models.CharField(max_length=30)

    class Meta:
        ordering = ["position"]
        verbose_name = "Standing"
        verbose_name_plural = "Standings"

    def __str__(self) -> str:
        return f"{self.position}. {self.team.name} - {self.points} pts"


class Gameweek(TimeStampedUUIDModel):
    number = models.PositiveIntegerField(default=1)
    start_date = models.DateField()
    end_date = models.DateField()
    transfer_deadline = models.DateTimeField()
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["number"]
        unique_together = ("number", "start_date")
        verbose_name = "Gameweek"
        verbose_name_plural = "Gameweeks"

    def __str__(self) -> str:
        return f"Gameweek {self.number}"

    def save(self, *args, **kwargs):
        if not self.pk and not self.number:
            max_number = (
                Gameweek.objects.aggregate(models.Max("number")).get("number__max") or 0
            )
            self.number = max_number + 1
        super().save(*args, **kwargs)


class Fixture(TimeStampedUUIDModel):
    home_team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="home_fixtures"
    )
    away_team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="away_fixtures"
    )
    match_date = models.DateTimeField()
    venue = models.CharField(max_length=255)
    gameweek = models.ForeignKey(
        Gameweek, on_delete=models.SET_NULL, null=True, blank=True
    )
    status = models.CharField(
        max_length=20, choices=FIXTURE_STATUS, default=FIXTURE_STATUS[0][1]
    )
    home_team_score = models.PositiveIntegerField(null=True, blank=True)
    away_team_score = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("home_team", "away_team", "match_date")
        ordering = ["match_date"]
        verbose_name = "Fixture"
        verbose_name_plural = "Fixtures"

    def __str__(self) -> str:
        return f"{self.home_team} vs {self.away_team} on {self.match_date}"


# Lineups and provider mappings
class ExternalTeamMapping(TimeStampedUUIDModel):
    provider = models.CharField(max_length=50)
    provider_team_id = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="external_ids")

    class Meta:
        unique_together = ("provider", "provider_team_id")
        verbose_name = "External Team Mapping"
        verbose_name_plural = "External Team Mappings"

    def __str__(self):
        return f"{self.provider}:{self.provider_team_id} -> {self.team.name}"


class ExternalFixtureMapping(TimeStampedUUIDModel):
    provider = models.CharField(max_length=50)
    provider_fixture_id = models.CharField(max_length=100)
    fixture = models.ForeignKey(
        Fixture, on_delete=models.CASCADE, related_name="external_ids"
    )

    class Meta:
        unique_together = ("provider", "provider_fixture_id")
        verbose_name = "External Fixture Mapping"
        verbose_name_plural = "External Fixture Mappings"

    def __str__(self):
        return f"{self.provider}:{self.provider_fixture_id} -> {self.fixture}"


SIDE_CHOICES = [
    ("home", "Home"),
    ("away", "Away"),
]


class FixtureLineup(TimeStampedUUIDModel):
    fixture = models.ForeignKey(
        Fixture, on_delete=models.CASCADE, related_name="lineups"
    )
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="lineups")
    side = models.CharField(max_length=10, choices=SIDE_CHOICES)
    formation = models.CharField(max_length=20, null=True, blank=True)
    is_confirmed = models.BooleanField(default=False)
    source = models.CharField(max_length=50, default="manual")
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("fixture", "team", "side")
        verbose_name = "Fixture Lineup"
        verbose_name_plural = "Fixture Lineups"

    def __str__(self) -> str:
        return f"{self.team.name} lineup ({self.side}) for {self.fixture}"


class FixtureLineupPlayer(TimeStampedUUIDModel):
    lineup = models.ForeignKey(
        FixtureLineup, on_delete=models.CASCADE, related_name="players"
    )
    player = models.ForeignKey(
        Player, on_delete=models.SET_NULL, null=True, blank=True, related_name="lineup_entries"
    )
    position = models.CharField(max_length=3, choices=POSITION_CHOICES, null=True, blank=True)
    order_index = models.PositiveIntegerField()
    is_bench = models.BooleanField(default=False)

    class Meta:
        unique_together = ("lineup", "order_index")
        ordering = ["lineup", "is_bench", "order_index"]
        verbose_name = "Fixture Lineup Player"
        verbose_name_plural = "Fixture Lineup Players"

    def __str__(self) -> str:
        return f"{self.player or 'Unknown'} ({'Bench' if self.is_bench else 'XI'})"


class PlayerAlias(TimeStampedUUIDModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="player_aliases")
    canonical_player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="aliases"
    )
    normalized_name = models.CharField(max_length=120)
    jersey_number = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("team", "normalized_name")
        indexes = [
            models.Index(fields=["team", "normalized_name"]),
        ]
        verbose_name = "Player Alias"
        verbose_name_plural = "Player Aliases"

    def __str__(self) -> str:
        return f"{self.normalized_name} -> {self.canonical_player.name} ({self.team.name})"
