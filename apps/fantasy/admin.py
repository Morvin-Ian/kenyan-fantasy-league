from django.contrib import admin
from django.utils.html import format_html

from .models import (
    FantasyLeague,
    FantasyPlayer,
    FantasyTeam,
    PlayerPerformance,
    PlayerTransfer,
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
        "gameweek"
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
