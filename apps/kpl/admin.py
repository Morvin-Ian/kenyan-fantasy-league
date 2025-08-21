from django.contrib import admin

from .models import Fixture, Gameweek, Player, Standing, Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "logo_url")
    search_fields = ("name",)


@admin.register(Standing)
class StandingAdmin(admin.ModelAdmin):
    list_display = (
        "position",
        "team",
        "played",
        "wins",
        "draws",
        "losses",
        "goals_for",
        "goals_against",
        "goal_differential",
        "points",
        "period",
    )
    list_filter = ("period", "team")
    search_fields = ("team__name",)


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("name", "team", "position", "jersey_number", "age", 'created_at')
    list_filter = ("team", "position")
    search_fields = ("name", "team__name")


@admin.register(Fixture)
class FixtureAdmin(admin.ModelAdmin):
    list_display = (
        "home_team",
        "away_team",
        "match_date",
        "venue",
        "status",
        "home_team_score",
        "away_team_score",
        'created_at'
    )
    list_filter = ("status", "match_date")
    search_fields = ("home_team__name", "away_team__name", "venue")


@admin.register(Gameweek)
class Gameweekdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "start_date",
        "end_date",
        "transfer_deadline",
        "is_active",
    )
    list_filter = ("number", "is_active")
    search_fields = ("number", "is_active")
