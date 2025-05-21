from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from apps.fantasy.models import FantasyTeam
from .serializers import FantasyTeamSerializer


class FantasyTeamViewSet(viewsets.ModelViewSet):
    queryset = FantasyTeam.objects.all()
    serializer_class = FantasyTeamSerializer
    permission_classes = [permissions.IsAuthenticated]
    