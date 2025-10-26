from django.contrib import admin

from .models import (
    Fixture,
    FixtureLineup,
    FixtureLineupPlayer,
    Gameweek,
    Player,
    Standing,
    Team,
    ProcessedMatchEvent, 
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


@admin.register(ProcessedMatchEvent)
class ProcessedMatchEventAdmin(admin.ModelAdmin):
    list_display = (
        "fixture_display",
        "event_type",
        "player_display",
        "minute",
        "event_key_short",
        "created_at",
    )
    
    list_filter = (
        "event_type",
        "fixture__gameweek",
        "fixture__status",
        "created_at",
    )
    
    search_fields = (
        "fixture__home_team__name",
        "fixture__away_team__name",
        "player__name",
        "event_type",
        "event_key",
    )
    
    readonly_fields = (
        "id",
        "created_at",
        "event_key",
    )
    
    fieldsets = (
        ("Basic Information", {
            "fields": (
                "fixture",
                "event_type",
                "player",
                "minute",
            )
        }),
        ("Technical Details", {
            "fields": (
                "event_key",
                "created_at",
            ),
            "classes": ("collapse",)
        }),
    )
    
    def fixture_display(self, obj):
        return f"{obj.fixture.home_team} vs {obj.fixture.away_team}"
    fixture_display.short_description = "Fixture"
    fixture_display.admin_order_field = "fixture"
    
    def player_display(self, obj):
        return f"{obj.player.name} ({obj.player.team})" if obj.player else "N/A"
    player_display.short_description = "Player"
    player_display.admin_order_field = "player__name"
    
    def event_key_short(self, obj):
        return obj.event_key[:50] + "..." if len(obj.event_key) > 50 else obj.event_key
    event_key_short.short_description = "Event Key (Short)"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'fixture', 
            'fixture__home_team', 
            'fixture__away_team', 
            'fixture__gameweek',
            'player',
            'player__team'
        )
    
    # Add some useful actions
    actions = [
        'delete_events_for_completed_fixtures',
        'export_events_to_csv',
    ]
    
    def delete_events_for_completed_fixtures(self, request, queryset):
        """Action to delete events for completed fixtures"""
        from django.db.models import Q
        
        completed_fixtures_events = ProcessedMatchEvent.objects.filter(
            Q(fixture__status='completed') | Q(fixture__status='cancelled')
        )
        count = completed_fixtures_events.count()
        completed_fixtures_events.delete()
        
        self.message_user(
            request,
            f"Successfully deleted {count} events for completed/cancelled fixtures.",
        )
    
    delete_events_for_completed_fixtures.short_description = "Delete events for completed fixtures"
    
    def export_events_to_csv(self, request, queryset):
        """Action to export selected events to CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="processed_match_events.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Fixture', 
            'Gameweek', 
            'Event Type', 
            'Player', 
            'Team', 
            'Minute', 
            'Event Key', 
            'Created At'
        ])
        
        for event in queryset.select_related('fixture', 'fixture__gameweek', 'player', 'player__team'):
            writer.writerow([
                f"{event.fixture.home_team} vs {event.fixture.away_team}",
                event.fixture.gameweek.number if event.fixture.gameweek else 'N/A',
                event.event_type,
                event.player.name if event.player else 'N/A',
                event.player.team.name if event.player and event.player.team else 'N/A',
                event.minute if event.minute else 'N/A',
                event.event_key,
                event.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        
        return response
    
    export_events_to_csv.short_description = "Export selected events to CSV"