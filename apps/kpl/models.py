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
    is_relagated = models.BooleanField(
        default=False,
        help_text="Indicates if the team has been relegated from the league",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Team"
        verbose_name_plural = "Teams"

    def __str__(self):
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

    def __str__(self):
        return f"{self.name} ({self.team.name}) - {self.get_position_display()}"


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

    def __str__(self):
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

    def __str__(self):
        return f"Gameweek {self.number}"

    def save(self, *args, **kwargs):
        if not self.pk and not self.number:
            max_number = (
                Gameweek.objects.aggregate(models.Max("number"))["number__max"] or 0
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

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} on {self.match_date}"
