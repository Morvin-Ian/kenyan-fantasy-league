from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from apps.kpl.models import Fixture, Gameweek, Player
from util.models import TimeStampedUUIDModel

User = get_user_model()

FORMATION_CHOICES = [
    ("3-4-3", "3-4-3"),
    ("3-5-2", "3-5-2"),
    ("4-4-2", "4-4-2"),
    ("4-3-3", "4-3-3"),
    ("5-3-2", "5-3-2"),
    ("5-2-3", "5-2-3"),
    ("5-4-1", "5-4-1"),
]


class ChipType(models.TextChoices):
    TRIPLE_CAPTAIN = 'TC', 'Triple Captain'
    BENCH_BOOST = 'BB', 'Bench Boost'
    WILDCARD = 'WC', 'Wildcard'


class FantasyTeam(TimeStampedUUIDModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="fantasy_teams"
    )
    name = models.CharField(max_length=100, unique=True)
    budget = models.DecimalField(max_digits=6, decimal_places=2, default=70.00)
    formation = models.CharField(
        max_length=10, choices=FORMATION_CHOICES, default="3-4-3"
    )
    free_transfers = models.PositiveIntegerField(default=1)
    total_points = models.PositiveIntegerField(default=0)
    overall_rank = models.PositiveIntegerField(null=True, blank=True)
    transfer_budget = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = "Fantasy Team"
        verbose_name_plural = "Fantasy Teams"

    def __str__(self):
        return f"{self.name} (Owner: {self.user.username})"


class Chip(TimeStampedUUIDModel):
    fantasy_team = models.ForeignKey(
        FantasyTeam, on_delete=models.CASCADE, related_name="chips"
    )
    chip_type = models.CharField(max_length=2, choices=ChipType.choices)
    is_used = models.BooleanField(default=False)
    used_in_gameweek = models.ForeignKey(
        Gameweek,
        on_delete=models.PROTECT,
        related_name="chips_used",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Chip"
        verbose_name_plural = "Chips"
        unique_together = ["fantasy_team", "chip_type"]
        indexes = [
            models.Index(fields=['fantasy_team', 'chip_type']),
            models.Index(fields=['is_used']),
        ]

    def __str__(self):
        status = f"Used in GW{self.used_in_gameweek.number}" if self.is_used else "Available"
        return f"{self.fantasy_team.name} - {self.get_chip_type_display()} ({status})"

    def clean(self):
        if self.is_used and not self.used_in_gameweek:
            raise ValidationError("Used chips must have a gameweek specified.")


class FantasyPlayer(TimeStampedUUIDModel):
    fantasy_team = models.ForeignKey(
        FantasyTeam, on_delete=models.CASCADE, related_name="players"
    )
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    total_points = models.PositiveIntegerField(default=0)
    is_captain = models.BooleanField(default=False)
    is_vice_captain = models.BooleanField(default=False)
    is_starter = models.BooleanField(default=True)
    purchase_price = models.DecimalField(max_digits=6, decimal_places=2)
    current_value = models.DecimalField(max_digits=6, decimal_places=2)
    gameweek_added = models.ForeignKey(
        Gameweek,
        on_delete=models.PROTECT,
        related_name="players_added",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Fantasy Player"
        verbose_name_plural = "Fantasy Players"
        unique_together = ["fantasy_team", "player"]
        indexes = [
            models.Index(fields=['fantasy_team', 'is_starter']),
            models.Index(fields=['player', 'fantasy_team']),
            models.Index(fields=['is_captain']),
            models.Index(fields=['is_vice_captain']),
        ]

    def __str__(self):
        return f"{self.player.name} - {self.fantasy_team.name}"

    def clean(self):
        if self.fantasy_team.players.count() >= 15 and not self.pk:
            raise ValidationError(
                "You can't have more than 15 players in a fantasy team."
            )

        same_team_players = self.fantasy_team.players.filter(
            player__team=self.player.team
        ).exclude(pk=self.pk)

        if same_team_players.count() > 3:
            raise ValidationError(
                "You can't select more than 3 players from a single real team."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class FantasyLeague(TimeStampedUUIDModel):
    name = models.CharField(max_length=100, unique=True)
    commissioner = models.ForeignKey(User, on_delete=models.CASCADE)
    teams = models.ManyToManyField(FantasyTeam, related_name="leagues")
    start_gameweek = models.PositiveIntegerField()
    end_gameweek = models.PositiveIntegerField()

    class Meta:
        verbose_name = "League"
        verbose_name_plural = "Leagues"

    def __str__(self):
        return f"{self.name} (GW{self.start_gameweek}-{self.end_gameweek}, {self.teams.count()} teams)"


class PlayerTransfer(TimeStampedUUIDModel):
    fantasy_team = models.ForeignKey(
        FantasyTeam, on_delete=models.CASCADE, related_name="transfers"
    )
    player_in = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="transfers_in"
    )
    player_out = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="transfers_out"
    )
    gameweek = models.ForeignKey(
        Gameweek, on_delete=models.PROTECT, null=True, blank=True
    )
    transfer_cost = models.DecimalField(max_digits=4, decimal_places=1, default=0)

    class Meta:
        verbose_name = "Player Transfer"
        verbose_name_plural = "Player Transfers"

    def __str__(self):
        return f"{self.fantasy_team.name}: {self.player_out.name} → {self.player_in.name} (GW {self.gameweek.number})"


class PlayerPerformance(TimeStampedUUIDModel):
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="performances",
        null=True,
        blank=True,
    )
    gameweek = models.ForeignKey(
        Gameweek,
        on_delete=models.PROTECT,
        related_name="player_performances",
        null=True,
        blank=True,
    )
    fixture = models.ForeignKey(
        Fixture,
        on_delete=models.PROTECT,
        related_name="performances",
        null=True,
        blank=True,
    )
    yellow_cards = models.PositiveIntegerField(default=0)
    red_cards = models.PositiveIntegerField(default=0)
    goals_scored = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    clean_sheets = models.PositiveIntegerField(default=0)
    saves = models.PositiveIntegerField(default=0)
    own_goals = models.PositiveIntegerField(default=0)
    penalties_saved = models.PositiveIntegerField(default=0)
    penalties_missed = models.PositiveIntegerField(default=0)
    minutes_played = models.PositiveIntegerField(default=0)
    fantasy_points = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Player Performance"
        verbose_name_plural = "Player Performances"
        unique_together = ["player", "fixture"]
        indexes = [
            models.Index(fields=['gameweek', '-fantasy_points']),
            models.Index(fields=['player', 'gameweek']),
            models.Index(fields=['-goals_scored']),
            models.Index(fields=['fixture']),
        ]

    def __str__(self):
        if self.player and self.fixture:
            return f"{self.player.name} - GW{self.fixture.gameweek.number} vs {self.fixture.away_team.name if self.player.team == self.fixture.home_team else self.fixture.home_team.name} ({self.goals_scored}G, {self.assists}A, {self.fantasy_points} pts)"
        return f"PlayerPerformance {self.id}"


class TeamSelection(TimeStampedUUIDModel):
    fantasy_team = models.ForeignKey(
        FantasyTeam, on_delete=models.CASCADE, related_name="selections"
    )
    gameweek = models.ForeignKey(
        Gameweek, on_delete=models.PROTECT, related_name="team_selections"
    )
    formation = models.CharField(max_length=10, choices=FORMATION_CHOICES)
    captain = models.ForeignKey(
        FantasyPlayer, on_delete=models.PROTECT, related_name="captain_selections"
    )
    vice_captain = models.ForeignKey(
        FantasyPlayer, on_delete=models.PROTECT, related_name="vice_captain_selections"
    )
    starters = models.ManyToManyField(FantasyPlayer, related_name="starter_selections")
    bench = models.ManyToManyField(FantasyPlayer, related_name="bench_selections")
    is_finalized = models.BooleanField(default=False)
    active_chip = models.CharField(
        max_length=2,
        choices=ChipType.choices,
        null=True,
        blank=True,
        help_text="Active chip for this gameweek (if any)"
    )

    class Meta:
        verbose_name = "Team Selection"
        verbose_name_plural = "Team Selections"
        unique_together = ["fantasy_team", "gameweek"]
        indexes = [
            models.Index(fields=['fantasy_team', 'gameweek', 'is_finalized']),
            models.Index(fields=['gameweek', 'is_finalized']),
            models.Index(fields=['active_chip']),
        ]

    def __str__(self):
        chip_info = f" [{self.get_active_chip_display()}]" if self.active_chip else ""
        return f"{self.fantasy_team.name} - GW{self.gameweek.number} ({self.formation}){chip_info}"

    def clean(self):
        """Validate team selection for the gameweek"""
        if self.starters.count() != 11:
            raise ValidationError("Must select exactly 11 starters.")

        if self.captain not in self.starters.all():
            raise ValidationError("Captain must be in starting lineup.")

        if self.vice_captain not in self.starters.all():
            raise ValidationError("Vice-captain must be in starting lineup.")
