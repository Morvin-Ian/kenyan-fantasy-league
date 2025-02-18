from django.db import models

class Team(models.Model):
    name = models.CharField(max_length=100)
    logo_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'KPL Team'
        verbose_name_plural = 'KPL Teams'
    
    def __str__(self):
        return self.name

class Standing(models.Model):
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
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position']
        verbose_name = 'KPL Standing'
        verbose_name_plural = 'KPL Standings'
    
    def __str__(self):
        return f"{self.position}. {self.team.name} - {self.points} pts"
