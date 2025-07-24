from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.fantasy.models import FantasyPlayer, FantasyTeam

from .serializers import FantasyPlayerSerializer, FantasyTeamSerializer
from .services import FantasyService


class FantasyTeamViewSet(ModelViewSet):
    queryset = FantasyTeam.objects.all()
    serializer_class = FantasyTeamSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def perform_create(self, serializer):
        user = self.request.user

        if FantasyTeam.objects.filter(user=user).exists():
            raise ValidationError(
                "You already have a fantasy team.", code=status.HTTP_400_BAD_REQUEST
            )

        team_name = serializer.validated_data.get("name")
        if team_name and FantasyTeam.objects.filter(name__iexact=team_name).exists():
            raise ValidationError(
                f"A team with the name '{team_name}' already exists.",
                code=status.HTTP_400_BAD_REQUEST,
            )
        return FantasyService.create_fantasy_team(user, serializer.validated_data)

    @action(detail=False, methods=["get"], url_path="user-team")
    def get_user_team(self, request):
        try:
            teams = FantasyTeam.objects.filter(user=request.user)
            serializer = self.get_serializer(teams, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": "An unexpected error occurred.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FantasyPlayerViewSet(ModelViewSet):
    queryset = FantasyPlayer.objects.all()
    serializer_class = FantasyPlayerSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    @action(detail=False, methods=["get"], url_path="team-players")
    def get_team_players(self, request):
        try:
            team = FantasyTeam.objects.filter(user=request.user)
            if team.exists():
                players = FantasyPlayer.objects.filter(fantasy_team=team.first())
                serializer = self.get_serializer(players, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"detail": "No fantasy team found for this user."},
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            return Response(
                {"detail": "An unexpected error occurred.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"], url_path="save-team-players")
    def save_team_players(self, request):
        try:
            starting_eleven = request.data.get("startingEleven", {})
            bench_players = request.data.get("benchPlayers", [])
            fantasy_team = FantasyTeam.objects.get(user=request.user)
            
            # Extract starting eleven data
            goalkeeper = starting_eleven.get("goalkeeper")
            defenders = starting_eleven.get("defenders", [])
            midfielders = starting_eleven.get("midfielders", [])
            forwards = starting_eleven.get("forwards", [])
            
            
            all_player_ids = []
            players_to_update = {}
            
            if goalkeeper:
                player_id = goalkeeper.get('player') or goalkeeper.get('id')
                all_player_ids.append(player_id)
                players_to_update[player_id] = {
                    'is_starter': True,
                    'is_captain': goalkeeper.get('is_captain', False),
                    'is_vice_captain': goalkeeper.get('is_vice_captain', False),
                    'purchase_price': goalkeeper.get('purchase_price', goalkeeper.get('price', 0)),
                    'current_value': goalkeeper.get('current_value', goalkeeper.get('price', 0)),
                }
            
            for position_players in [defenders, midfielders, forwards]:
                for player_data in position_players:
                    player_id = player_data.get('player') or player_data.get('id')
                    all_player_ids.append(player_id)
                    players_to_update[player_id] = {
                        'is_starter': True,
                        'is_captain': player_data.get('is_captain', False),
                        'is_vice_captain': player_data.get('is_vice_captain', False),
                        'purchase_price': player_data.get('purchase_price', player_data.get('price', 0)),
                        'current_value': player_data.get('current_value', player_data.get('price', 0)),
                    }
            
            # Process bench players
            for player_data in bench_players:
                player_id = player_data.get('player') or player_data.get('id')
                all_player_ids.append(player_id)
                players_to_update[player_id] = {
                    'is_starter': False,
                    'is_captain': False,
                    'is_vice_captain': False,
                    'purchase_price': player_data.get('purchase_price', player_data.get('price', 0)),
                    'current_value': player_data.get('current_value', player_data.get('price', 0)),
                }
            
            fantasy_team.players.exclude(player__id__in=all_player_ids).delete()
            
            existing_players = {
                str(fp.player.id): fp for fp in fantasy_team.players.filter(player__id__in=all_player_ids)
            }
            
            players_to_create = []
            players_to_bulk_update = []
            
            for player_id, update_data in players_to_update.items():
                player_id_str = str(player_id) 
                if player_id_str in existing_players:
                    # Update existing player
                    fantasy_player = existing_players[player_id_str]
                    for field, value in update_data.items():
                        setattr(fantasy_player, field, value)
                    players_to_bulk_update.append(fantasy_player)
                else:
                    print(update_data)
                    try:
                        from apps.kpl.models import Player  
                        player_instance = Player.objects.get(id=player_id)
                        fantasy_player = FantasyPlayer(
                            fantasy_team=fantasy_team,
                            player=player_instance,  
                            total_points=0,
                            gameweek_added=fantasy_team.current_gameweek,
                            **update_data
                        )
                        players_to_create.append(fantasy_player)
                    except Player.DoesNotExist:
                        continue
            
            if players_to_create:
                FantasyPlayer.objects.bulk_create(players_to_create)
            
            if players_to_bulk_update:
                FantasyPlayer.objects.bulk_update(
                    players_to_bulk_update,
                    ['is_starter', 'is_captain', 'is_vice_captain', 'purchase_price', 'current_value']
                )
            
            fantasy_team.clean()
            
            return Response({
                "detail": "Players updated successfully.",
                "players_created": len(players_to_create),
                "players_updated": len(players_to_bulk_update)
            }, status=status.HTTP_200_OK)
            
        except FantasyTeam.DoesNotExist:
            return Response(
                {"detail": "Fantasy team not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response(
                {"detail": "Validation error occurred.", "errors": e.message_dict if hasattr(e, 'message_dict') else str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"detail": "An unexpected error occurred.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )