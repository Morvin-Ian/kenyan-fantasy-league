from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

from .models import (
    FantasyLeague,
    FantasyPlayer,
    FantasyTeam,
    PlayerPerformance,
    PlayerTransfer,
    TeamSelection,
)


@admin.register(FantasyTeam)
class FantasyTeamAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "owner_display",
        "formation",
        "total_points",
        "budget_display",
    )
    list_filter = ("formation", "name")
    search_fields = ("name", "user__username", "user__email")

    def owner_display(self, obj):
        return obj.user.username

    owner_display.short_description = "Owner"

    def budget_display(self, obj):
        if float(obj.budget) < 20.0:
            color = "red"
        elif float(obj.budget) < 50.0:
            color = "orange"
        else:
            color = "green"
        return format_html('<span style="color: {};">£{}</span>', color, obj.budget)

    budget_display.short_description = "Budget"


class FantasyPlayerInline(admin.TabularInline):
    model = FantasyPlayer
    extra = 0
    fields = (
        "player",
        "is_starter",
        "is_captain",
        "is_vice_captain",
        "purchase_price",
        "current_value",
    )
    readonly_fields = ("player",)
    can_delete = False


@admin.register(FantasyPlayer)
class FantasyPlayerAdmin(admin.ModelAdmin):
    list_display = (
        "player_name",
        "fantasy_team_name",
        "gameweek_added",
        "is_starter",
        "captain_status",
        "points_display",
    )
    list_filter = ("is_starter", "is_captain", "is_vice_captain", "gameweek_added")
    search_fields = ("player__name", "fantasy_team__name")

    def player_name(self, obj):
        return obj.player.name

    player_name.short_description = "Player"

    def fantasy_team_name(self, obj):
        return obj.fantasy_team.name

    fantasy_team_name.short_description = "Team"

    def captain_status(self, obj):
        if obj.is_captain:
            return format_html('<span style="color: gold;">✦✦ Captain</span>')
        elif obj.is_vice_captain:
            return format_html('<span style="color: silver;">✦ Vice</span>')
        return "-"

    captain_status.short_description = "Role"

    def points_display(self, obj):
        return format_html("<b>{}</b>", obj.total_points)

    points_display.short_description = "Points"


class PlayerPerformanceInline(admin.TabularInline):
    model = PlayerPerformance
    extra = 0
    fields = (
        "minutes_played",
        "goals_scored",
        "assists",
        "clean_sheets",
        "yellow_cards",
        "red_cards",
    )


@admin.register(PlayerPerformance)
class PlayerPerformanceAdmin(admin.ModelAdmin):
    list_display = (
        "player_name",
        "team_name",
        "minutes_played",
        "goals_scored",
        "assists",
        "yellow_card_display",
        "red_card_display",
        "gameweek",
    )
    list_filter = ("yellow_cards", "red_cards")
    search_fields = ("player__name",)

    def player_name(self, obj):
        return obj.player.name

    player_name.short_description = "Player"

    def team_name(self, obj):
        return obj.player.team.name

    team_name.short_description = "Team"

    def yellow_card_display(self, obj):
        if obj.yellow_cards > 0:
            return format_html(
                '<span style="color: #FFD700;">●</span> ' * obj.yellow_cards
            )
        return "-"

    yellow_card_display.short_description = "Yellow Cards"

    def red_card_display(self, obj):
        if obj.red_cards > 0:
            return format_html('<span style="color: red;">●</span> ' * obj.red_cards)
        return "-"

    red_card_display.short_description = "Red Cards"


@admin.register(PlayerTransfer)
class PlayerTransferAdmin(admin.ModelAdmin):
    list_display = (
        "transfer_display",
        "fantasy_team",
        "gameweek_display",
        "transfer_cost_display",
    )
    list_filter = ("gameweek", "transfer_cost")
    search_fields = ("fantasy_team__name", "player_in__name", "player_out__name")

    def transfer_display(self, obj):
        return format_html(
            '{} <span style="color: #888;">→</span> {}',
            obj.player_out.name,
            obj.player_in.name,
        )

    transfer_display.short_description = "Transfer"

    def gameweek_display(self, obj):
        return f"GW {obj.gameweek.number}"

    gameweek_display.short_description = "Gameweek"

    def transfer_cost_display(self, obj):
        if obj.transfer_cost > 0:
            return format_html(
                '<span style="color: red;">-{}</span>', obj.transfer_cost
            )
        return "0"

    transfer_cost_display.short_description = "Cost"


@admin.register(FantasyLeague)
class FantasyLeagueAdmin(admin.ModelAdmin):
    list_display = ("name", "commissioner_display", "gameweek_range", "teams_count")
    search_fields = ("name", "commissioner__username")
    filter_horizontal = ("teams",)

    def commissioner_display(self, obj):
        return obj.commissioner.username

    commissioner_display.short_description = "Commissioner"

    def gameweek_range(self, obj):
        return f"GW {obj.start_gameweek} - {obj.end_gameweek}"

    gameweek_range.short_description = "Duration"

    def teams_count(self, obj):
        count = obj.teams.count()
        return format_html('<span style="font-weight: bold;">{}</span>', count)

    teams_count.short_description = "Teams"


@admin.register(TeamSelection)
class TeamSelectionAdmin(admin.ModelAdmin):
    list_display = (
        "team_name_display",
        "gameweek_display",
        "formation_display",
        "captain_display",
        "vice_captain_display",
        "starters_count",
        "last_updated",
    )
    list_filter = ("gameweek", "formation", "is_finalized", "fantasy_team")
    search_fields = ("fantasy_team__name", "fantasy_team__user__username")
    readonly_fields = (
        "created_at",
        "updated_at",
        "starters_preview",
        "bench_preview",
    )
    filter_horizontal = ("starters",)

    fieldsets = (
        (
            "Team Information",
            {"fields": ("fantasy_team", "gameweek", "formation", "is_finalized")},
        ),
        ("Captain Choices", {"fields": ("captain", "vice_captain")}),
        (
            "Starting Lineup",
            {
                "fields": ("starters", "starters_preview"),
                "description": "Select exactly 11 players for the starting lineup",
            },
        ),
        ("Bench Players", {"fields": ("bench_preview",), "classes": ("collapse",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def team_name_display(self, obj):
        return format_html(
            '<strong>{}</strong><br><small style="color: #666;">{}</small>',
            obj.fantasy_team.name,
            obj.fantasy_team.user.username,
        )

    team_name_display.short_description = "Fantasy Team"

    def gameweek_display(self, obj):
        if hasattr(obj.gameweek, "deadline"):
            deadline_passed = (
                timezone.now() > obj.gameweek.deadline
                if obj.gameweek.deadline
                else False
            )
            if deadline_passed:
                color = "#888"
                icon = "🔒"
            else:
                color = "#4CAF50"
                icon = "✓"
            return format_html(
                '<span style="color: {};">{} GW {}</span>',
                color,
                icon,
                obj.gameweek.number,
            )
        return f"GW {obj.gameweek.number}"

    gameweek_display.short_description = "Gameweek"

    def formation_display(self, obj):
        return format_html(
            '<span style=" padding: 4px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            obj.formation,
        )

    formation_display.short_description = "Formation"

    def captain_display(self, obj):
        if obj.captain:
            return format_html(
                '<span style="color: gold;">✦✦</span> {}<br><small style="color: #666;">{}</small>',
                obj.captain.player.name,
                obj.captain.player.position,
            )
        return "-"

    captain_display.short_description = "Captain"

    def vice_captain_display(self, obj):
        if obj.vice_captain:
            return format_html(
                '<span style="color: silver;">✦</span> {}<br><small style="color: #666;">{}</small>',
                obj.vice_captain.player.name,
                obj.vice_captain.player.position,
            )
        return "-"

    vice_captain_display.short_description = "Vice Captain"

    def starters_count(self, obj):
        count = obj.starters.count()
        if count == 11:
            color = "green"
            icon = "✓"
        else:
            color = "red"
            icon = "✗"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}/11</span>',
            color,
            icon,
            count,
        )

    starters_count.short_description = "Starters"

    def last_updated(self, obj):
        return format_html(
            '<span title="{}">{}</span>',
            obj.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            obj.updated_at.strftime("%b %d, %H:%M"),
        )

    last_updated.short_description = "Last Updated"

    def starters_preview(self, obj):
        if not obj.pk:
            return "-"

        starters = obj.starters.all().select_related("player", "player__team")
        if not starters:
            return format_html('<p style="color: #999;">No starters selected yet</p>')

        positions = {"GKP": [], "DEF": [], "MID": [], "FWD": []}
        for fp in starters:
            positions[fp.player.position].append(fp)

        html = '<div style="font-family: monospace;">'
        position_names = {
            "GKP": "Goalkeepers",
            "DEF": "Defenders",
            "MID": "Midfielders",
            "FWD": "Forwards",
        }

        for pos_code, pos_name in position_names.items():
            players = positions[pos_code]
            if players:
                html += f'<p style="margin: 8px 0; font-weight: bold; color: #1976d2;">{pos_name} ({len(players)})</p>'
                for fp in players:
                    captain_badge = ""
                    if fp == obj.captain:
                        captain_badge = '<span style="color: gold;">✦✦</span> '
                    elif fp == obj.vice_captain:
                        captain_badge = '<span style="color: silver;">✦</span> '

                    html += f'<div style="margin-left: 16px; padding: 4px 0;">'
                    html += f"{captain_badge}{fp.player.name} "
                    html += f'<small style="color: #666;">({fp.player.team.name if fp.player.team else "N/A"})</small>'
                    html += f"</div>"

        html += "</div>"
        return format_html(html)

    starters_preview.short_description = "Starting XI Preview"

    def bench_preview(self, obj):
        if not obj.pk:
            return "-"

        all_players = obj.fantasy_team.players.all().select_related(
            "player", "player__team"
        )
        starters = obj.starters.all()
        bench = all_players.exclude(id__in=[s.id for s in starters])

        if not bench:
            return format_html('<p style="color: #999;">No bench players</p>')

        html = '<div style="font-family: monospace;">'
        html += '<p style="margin: 8px 0; font-weight: bold; color: #666;">🪑 Bench Players</p>'

        for fp in bench:
            html += f'<div style="margin-left: 16px; padding: 4px 0;">'
            html += f"{fp.player.name} ({fp.player.position}) "
            html += f'<small style="color: #666;">- {fp.player.team.name if fp.player.team else "N/A"}</small>'
            html += f"</div>"

        html += "</div>"
        return format_html(html)

    bench_preview.short_description = "Bench Preview"

    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related(
            "fantasy_team",
            "fantasy_team__user",
            "gameweek",
            "captain",
            "captain__player",
            "vice_captain",
            "vice_captain__player",
        ).prefetch_related("starters", "starters__player")
