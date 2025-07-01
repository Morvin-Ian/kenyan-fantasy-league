from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from apps.kpl.models import Gameweek, Player
from util.models import TimeStampedUUIDModel

User = get_user_model()

FORMATION_CHOICES = [
    ("3-4-3", "3-4-3"),
    ("3-5-2", "3-5-2"),
    ("4-4-2", "4-4-2"),
    ("4-3-3", "4-3-3"),
    ("5-3-2", "5-3-2"),
    ("5-4-1", "5-4-1"),
]


class FantasyTeam(TimeStampedUUIDModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="fantasy_teams"
    )
    name = models.CharField(max_length=100, unique=True)
    budget = models.DecimalField(max_digits=6, decimal_places=2, default=100.00)
    gameweek = models.PositiveIntegerField(default=1)
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

    # def clean(self):
    #     formation_map = {
    #         '3-4-3': {'DEF': 3, 'MID': 4, 'FWD': 3, 'GK': 1},
    #         '3-5-2': {'DEF': 3, 'MID': 5, 'FWD': 2, 'GK': 1},
    #         '4-4-2': {'DEF': 4, 'MID': 4, 'FWD': 2, 'GK': 1},
    #         '4-3-3': {'DEF': 4, 'MID': 3, 'FWD': 3, 'GK': 1},
    #         '5-3-2': {'DEF': 5, 'MID': 3, 'FWD': 2, 'GK': 1},
    #         '5-4-1': {'DEF': 5, 'MID': 4, 'FWD': 1, 'GK': 1},
    #     }

    #     if not self._state.adding and self.players.exists():
    #         position_counts = {}
    #         for player in self.players.all():
    #             pos = player.player.position
    #             position_counts[pos] = position_counts.get(pos, 0) + 1

    #         required = formation_map[self.formation]
    #         for pos, required_count in required.items():
    #             actual_count = position_counts.get(pos, 0)
    #             if actual_count != required_count:
    #                 raise ValidationError(f"Formation {self.formation} requires {required_count} {pos} players, you have {actual_count}")

    #     total_value = sum(
    #         float(p.current_value)
    #         for p in self.players.all()
    #     )
    #     if total_value > float(self.budget):
    #         raise ValidationError("Team value exceeds budget")


class FantasyPlayer(TimeStampedUUIDModel):
    fantasy_team = models.ForeignKey(
        FantasyTeam, on_delete=models.CASCADE, related_name="players"
    )
    player = models.ForeignKey(Player, on_delete=models.DO_NOTHING)
    gameweek = models.ForeignKey(
        Gameweek, on_delete=models.CASCADE, related_name="fantasy_players"
    )
    total_points = models.PositiveIntegerField(default=0)
    gameweek_points = models.PositiveIntegerField(default=0)
    is_captain = models.BooleanField(default=False)
    is_vice_captain = models.BooleanField(default=False)
    is_starter = models.BooleanField(default=True)
    purchase_price = models.DecimalField(max_digits=6, decimal_places=2)
    current_value = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        verbose_name = "Fantasy Player"
        verbose_name_plural = "Fantasy Players"

    def __str__(self):
        return (
            f"{self.player.name} - {self.fantasy_team.name} (GW {self.gameweek.number})"
        )

    def clean(self):
        if self.fantasy_team.players.count() >= 15 and not self.pk:
            raise ValidationError(
                "You can't have more than 15 players in a fantasy team."
            )

        same_team_players = self.fantasy_team.players.filter(
            player__team=self.player.team
        ).exclude(pk=self.pk)

        if same_team_players.count() >= 3:
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
    gameweek = models.ForeignKey(Gameweek, on_delete=models.CASCADE)
    transfer_cost = models.DecimalField(max_digits=4, decimal_places=1, default=0)

    class Meta:
        verbose_name = "Player Transfer"
        verbose_name_plural = "Player Transfers"

    def __str__(self):
        return f"{self.fantasy_team.name}: {self.player_out.name} → {self.player_in.name} (GW {self.gameweek.number})"


class PlayerPerformance(TimeStampedUUIDModel):
    fantasy_player = models.ForeignKey(
        FantasyPlayer, on_delete=models.CASCADE, related_name="performances"
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

    class Meta:
        verbose_name = "Player Performance"
        verbose_name_plural = "Players Performance"

    def __str__(self):
        return f"{self.fantasy_player.player.name} - GW{self.fantasy_player.gameweek.number} ({self.goals_scored}G, {self.assists}A, {self.minutes_played}min)"
