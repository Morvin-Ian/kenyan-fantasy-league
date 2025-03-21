from django.db import models
from util.models import TimeStampedUUIDModel


FIXTURE_STATUS = [
    ('upcoming', 'Upcoming'),
    ('live', 'Live'),
    ('postponed', 'Postponed'),
    ('completed', 'Completed'),
]

POSITION_CHOICES = [
    ('GKP', 'Goalkeeper'),
    ('DEF', 'Defender'),
    ('MID', 'Midfielder'),
    ('FWD', 'Foward'),
]

class Team(TimeStampedUUIDModel):
    name = models.CharField(max_length=100)
    logo_url = models.URLField()
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'
    
    def __str__(self):
        return self.name
    
class Player(TimeStampedUUIDModel):
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    jersey_number = models.PositiveIntegerField()
    age = models.PositiveIntegerField()

    class Meta:
        ordering = ['name']
        verbose_name = "Player"
        verbose_name_plural = "Players"

    def __str__(self):
        return f"{self.name} ({self.team.name}) - {self.get_position_display()}"

class Standing(TimeStampedUUIDModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='standings')
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
        ordering = ['position']
        verbose_name = 'Standing'
        verbose_name_plural = 'Standings'
    
    def __str__(self):
        return f"{self.position}. {self.team.name} - {self.points} pts"

class Fixture(TimeStampedUUIDModel):
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_fixtures')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_fixtures')
    match_date = models.DateTimeField()
    venue = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=FIXTURE_STATUS, default=FIXTURE_STATUS[0][1])
    home_team_score = models.PositiveIntegerField(null=True, blank=True)
    away_team_score = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['match_date']
        verbose_name = "Fixture"
        verbose_name_plural = "Fixtures"


    def __str__(self):
        return f"{self.home_team} vs {self.away_team} on {self.match_date}"