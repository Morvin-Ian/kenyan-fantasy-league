# from django.db import models
# from django.contrib.auth.models import User
# from django.core.validators import MinValueValidator, MaxValueValidator

# POSITION_CHOICES = [
#     ('GK', 'Goalkeeper'),
#     ('DF', 'Defender'),
#     ('MF', 'Midfielder'),
#     ('FW', 'Forward')
# ]

# class Team(models.Model):
#     name = models.CharField(max_length=100, unique=True)
#     city = models.CharField(max_length=100)
#     founded_year = models.PositiveIntegerField(validators=[MinValueValidator(1800), MaxValueValidator(2100)])
#     logo = models.ImageField(upload_to='team_logos/', blank=True, null=True)

#     def __str__(self):
#         return f"{self.name} ({self.city})"

# class Player(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name='players')
#     jersey_number = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(99)])
#     position = models.CharField(max_length=2, choices=POSITION_CHOICES)
#     price = models.DecimalField(max_digits=5, decimal_places=1, default=5.0)

#     def __str__(self):
#         return f"{self.user.get_full_name()} - {self.team.name} - {self.get_position_display()}"

# class Coach(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name='coaches')
#     role = models.CharField(max_length=100)
#     start_date = models.DateField()

#     def __str__(self):
#         return f"{self.user.get_full_name()} - {self.role} ({self.team.name})"

# class Gameweek(models.Model):
#     number = models.PositiveIntegerField(unique=True)
#     is_active = models.BooleanField(default=False)
#     deadline = models.DateTimeField()

#     def __str__(self):
#         return f"Gameweek {self.number}"

#     class Meta:
#         ordering = ['number']

# class Match(models.Model):
#     home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches')
#     away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches')
#     gameweek = models.ForeignKey(Gameweek, on_delete=models.CASCADE, related_name='matches')
#     date = models.DateTimeField()
#     venue = models.CharField(max_length=200)
#     home_score = models.PositiveIntegerField(null=True, blank=True)
#     away_score = models.PositiveIntegerField(null=True, blank=True)

#     def __str__(self):
#         return f"{self.home_team.name} vs {self.away_team.name} - GW{self.gameweek.number}"

#     class Meta:
#         unique_together = ('home_team', 'away_team', 'gameweek')

# class PlayerStatistics(models.Model):
#     player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='statistics')
#     gameweek = models.ForeignKey(Gameweek, on_delete=models.CASCADE)
#     minutes_played = models.PositiveIntegerField(default=0)
#     goals_scored = models.PositiveIntegerField(default=0)
#     assists = models.PositiveIntegerField(default=0)
#     clean_sheet = models.BooleanField(default=False)
#     goals_conceded = models.PositiveIntegerField(default=0)
#     yellow_cards = models.PositiveIntegerField(default=0)
#     red_cards = models.PositiveIntegerField(default=0)
#     penalty_saves = models.PositiveIntegerField(default=0)
#     penalty_misses = models.PositiveIntegerField(default=0)
#     saves = models.PositiveIntegerField(default=0)
#     own_goals = models.PositiveIntegerField(default=0)
#     bonus_points = models.PositiveIntegerField(default=0)
#     total_points = models.PositiveIntegerField(default=0)

#     def __str__(self):
#         return f"{self.player.user.get_full_name()} - GW{self.gameweek.number}"

#     class Meta:
#         unique_together = ("player", "gameweek")