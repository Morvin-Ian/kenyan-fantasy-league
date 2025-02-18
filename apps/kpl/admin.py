from django.contrib import admin
from .models import Team, Standing

# Register your models here.

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo_url', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(Standing)
class StandingAdmin(admin.ModelAdmin):
    list_display = ('position', 'team', 'played', 'wins', 'draws', 'losses', 'goals_for', 'goals_against', 'goal_differential', 'points', 'period')
    list_filter = ('period', 'team')
    search_fields = ('team__name',)
