from django.contrib import admin

from .models import (
    ExternalFixtureMapping,
    ExternalTeamMapping,
    Fixture,
    FixtureLineup,
    FixtureLineupPlayer,
    Gameweek,
    Player,
    Standing,
    Team,
)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "logo_url", "is_relegated")
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
    list_display = ("name", "team", "position", "jersey_number", "age", "created_at")
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
        "gameweek",
    )
    list_filter = ("status", "match_date")
    search_fields = ("home_team__name", "away_team__name", "venue")
    actions = [
        "filter_missing_lineups_near_ko",
    ]

    def filter_missing_lineups_near_ko(self, request, queryset):
        from datetime import timedelta

        from django.utils import timezone

        now = timezone.now()
        window_start = now
        window_end = now + timedelta(hours=3)
        qs = queryset.filter(match_date__gte=window_start, match_date__lte=window_end)
        ids = []
        for f in qs.prefetch_related("lineups"):
            has_home = any(l.side == "home" for l in f.lineups.all())
            has_away = any(l.side == "away" for l in f.lineups.all())
            if not (has_home and has_away):
                ids.append(str(f.id))
        self.message_user(
            request,
            f"Fixtures missing lineups in next 3h: {', '.join(ids) if ids else 'None'}",
        )

    filter_missing_lineups_near_ko.short_description = (
        "Report fixtures missing lineups (next 3h)"
    )


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


class FixtureLineupPlayerInline(admin.TabularInline):
    model = FixtureLineupPlayer
    extra = 0


@admin.register(FixtureLineup)
class FixtureLineupAdmin(admin.ModelAdmin):
    list_display = (
        "fixture",
        "team",
        "side",
        "formation",
        "is_confirmed",
        "source",
        "published_at",
    )
    list_filter = ("is_confirmed", "source", "side")
    search_fields = (
        "fixture__home_team__name",
        "fixture__away_team__name",
        "team__name",
    )
    inlines = [FixtureLineupPlayerInline]


# @admin.register(ExternalTeamMapping)
# class ExternalTeamMappingAdmin(admin.ModelAdmin):
#     list_display = ("provider", "provider_team_id", "team")
#     list_filter = ("provider",)
#     search_fields = ("provider", "provider_team_id", "team__name")


# @admin.register(ExternalFixtureMapping)
# class ExternalFixtureMappingAdmin(admin.ModelAdmin):
#     list_display = ("provider", "provider_fixture_id", "fixture")
#     list_filter = ("provider",)
#     search_fields = (
#         "provider",
#         "provider_fixture_id",
#         "fixture__home_team__name",
#         "fixture__away_team__name",
#     )
