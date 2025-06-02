from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from core.models import Game, Invitation, StatusChoices, TournamentStatusChoices, Winrate
from shared_models.models import Player, Match, Tournament
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models import Q
from . import serializers
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse

@method_decorator(csrf_exempt, name='dispatch')
class StatusApi(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({"code": 1000})

@method_decorator(csrf_exempt, name='dispatch')
class InvitationListAPI(generics.ListAPIView):
    """
    Liste les invitations en attente destinées au joueur connecté.
    - GET /pong/invitations/ : Liste les invitations reçues en attente pour l'utilisateur.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.PongInvitationSerializer

    def get_queryset(self):
        try:
            player = Player.objects.get(user=self.request.user)
        except Player.DoesNotExist:
            raise serializers.ValidationError({"code": 4001, "message": "No player profile associated with the user"})  # Aucun profil joueur associé à l'utilisateur
        return Invitation.objects.filter(to_player=player, status=StatusChoices.EN_ATTENTE) | Invitation.objects.filter(from_player=player, status=StatusChoices.EN_ATTENTE)
    
@method_decorator(csrf_exempt, name='dispatch')
class InvitationCreateAPI(generics.CreateAPIView):
    """
    Crée une nouvelle invitation.
    - POST /pong/invitations/create/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.PongInvitationSerializer

@method_decorator(csrf_exempt, name='dispatch')
class InvitationCancelAPI(generics.UpdateAPIView):
    """
    Permet à from_player d'annuler une invitation qu'il a envoyée.
    - POST /pong/invitations/<id>/cancel/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.InvitationCancelSerializer
    queryset = Invitation.objects.all()
    lookup_field = 'id'
    
@method_decorator(csrf_exempt, name='dispatch')
class InvitationAcceptAPI(generics.UpdateAPIView):
    """
    Permet à player_2 d'accepter une invitation.
    - POST /pong/invitations/<id>/accept/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.InvitationAcceptSerializer
    queryset = Invitation.objects.all()
    lookup_field = 'id'


@method_decorator(csrf_exempt, name='dispatch')   
class InvitationDeclineAPI(generics.UpdateAPIView):
    """
    Permet à player_2 de refuser une invitation.
    - POST /pong/invitations/<id>/decline/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.InvitationDeclineSerializer
    queryset = Invitation.objects.all()
    lookup_field = 'id'

@method_decorator(csrf_exempt, name='dispatch')
class WinrateAPI(generics.RetrieveAPIView):
    """
    Récupère les statistiques de Winrate d'un joueur.
    - GET /pong/winrate/ : Récupère le winrate de l'utilisateur authentifié.
    - GET /pong/winrate/?player_id=<id> : Récupère le winrate d'un joueur spécifique.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.WinrateSerializer
    
    def get_object(self):
        player_id = self.request.query_params.get('player_id')
        
        if player_id:
            try:
                player = Player.objects.get(id=player_id)
            except Player.DoesNotExist:
                raise serializers.ValidationError({"code": 4101, "message": "player search not found"}) #joueur rechercher introuvable
        else:
            try:
                player = Player.objects.get(user=self.request.user)
            except Player.DoesNotExist:
                raise serializers.ValidationError({"code": 4001, "message": "player login not found"}) #joueur connecter introuvable
        
        # Récupérer ou créer le winrate pour le joueur
        winrate, _ = Winrate.objects.get_or_create(player=player)
        return winrate

@method_decorator(csrf_exempt, name='dispatch')
class MatchListAPI(generics.ListAPIView):
    """
    Liste les matchs où l'utilisateur est impliqué.
    - GET /pong/matches/ : Liste les matchs de l'utilisateur authentifié.
    - GET /pong/matches/?player_id=<id> : Liste les matchs d'un joueur spécifique.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.PongMatchSerializer

    def get_queryset(self):
        player_id = self.request.query_params.get('player_id')
        if player_id:
            try:
                player = Player.objects.get(id=player_id)
            except Player.DoesNotExist:
                raise serializers.ValidationError({"code": 4101, "message": "player search not found"})
            return Match.objects.filter(player_1=player) | Match.objects.filter(player_2=player)
        player = Player.objects.get(user=self.request.user)
        return Match.objects.filter(player_1=player) | Match.objects.filter(player_2=player)

@method_decorator(csrf_exempt, name='dispatch')
class MatchDetailAPI(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.PongMatchSerializer
    lookup_field = 'id'

    def get_queryset(self):
        player = Player.objects.get(user=self.request.user)
        return Match.objects.filter(player_1=player) | Match.objects.filter(player_2=player)

@method_decorator(csrf_exempt, name='dispatch')
class GameDetailAPI(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.PongGameSerializer
    lookup_field = 'id'

    def get_queryset(self):
        match_id = self.kwargs['match_id']
        player = Player.objects.get(user=self.request.user)
        games = Game.objects.filter(match_id=match_id)
        return games.filter(player_1=player) | games.filter(player_2=player)

#---------------------------------------------------------#

@method_decorator(csrf_exempt, name='dispatch')
class TournamentCreateAPI(generics.CreateAPIView):
    serializer_class = serializers.TournamentCreateSerializer
    permission_classes = [IsAuthenticated]

@method_decorator(csrf_exempt, name='dispatch')
class TournamentOpenListAPI(generics.ListAPIView):
    serializer_class = serializers.TournamentListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Tournament.objects.filter(status=TournamentStatusChoices.OUVERT)
    
@method_decorator(csrf_exempt, name='dispatch')
class TournamentHistoryListAPI(generics.ListAPIView):
    serializer_class = serializers.TournamentListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        player_id = self.kwargs.get('id')
        return Tournament.objects.filter(
            Q(player_1_id=player_id) | 
            Q(player_2_id=player_id) | 
            Q(player_3_id=player_id) | 
            Q(player_4_id=player_id),
            status=TournamentStatusChoices.TERMINE
        )

@method_decorator(csrf_exempt, name='dispatch')
class TournamentMatchListAPI(generics.ListAPIView):
    serializer_class = serializers.TournamentMatchSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        tournament_id = self.kwargs.get('tournament_id')
        return Game.objects.filter(tournament_id=tournament_id)

@method_decorator(csrf_exempt, name='dispatch')
class TournamentJoinAPI(generics.UpdateAPIView):
    serializer_class = serializers.TournamentJoinSerializer
    permission_classes = [IsAuthenticated]
    queryset = Tournament.objects.all()
    lookup_field = 'id'

@method_decorator(csrf_exempt, name='dispatch')
class TournamentStartAPI(generics.UpdateAPIView):
    queryset = Tournament.objects.all()
    serializer_class = serializers.TournamentStartSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_object(self):
        """Récupère le tournoi par ID."""
        return super().get_object()

@method_decorator(csrf_exempt, name='dispatch')  
class TournamentStartFinalAPI(generics.UpdateAPIView):
    queryset = Tournament.objects.all()
    serializer_class = serializers.TournamentStartFinalSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_object(self):
        """Récupère le tournoi par ID."""
        return super().get_object()

@method_decorator(csrf_exempt, name='dispatch')
class TournamentEndAPI(generics.UpdateAPIView):
    queryset = Tournament.objects.all()
    serializer_class = serializers.TournamentEndSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_object(self):
        """Récupère le tournoi par ID."""
        return super().get_object()

@method_decorator(csrf_exempt, name='dispatch')
class TournamentLeaveAPI(generics.UpdateAPIView):
    queryset = Tournament.objects.all()
    serializer_class = serializers.TournamentLeaveSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_object(self):
        """Récupère le tournoi par ID."""
        return super().get_object()

@method_decorator(csrf_exempt, name='dispatch')
class TournamentGetIdAPI(generics.GenericAPIView):
    """
    Récupère l'ID d'un tournoi.
    - GET /pong/tournaments/get-id/ : Retourne l'ID du tournoi.
    """
    serializer_class = serializers.TournamentGetIdSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.to_representation(serializer.validated_data))

@method_decorator(csrf_exempt, name='dispatch')
class TournamentSeeFinalistsAPI(generics.GenericAPIView):
    """
    Récupère les finalistes d’un tournoi en cours.
    - GET /pong/tournaments/<id>/finalists/ : Retourne les deux finalistes du tournoi spécifié.
    """
    serializer_class = serializers.TournamentSeeFinalSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    queryset = Tournament.objects.all()

    def get(self, request, *args, **kwargs):
        tournament = self.get_object()
        serializer = self.get_serializer(instance=tournament, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.to_representation(tournament))

@method_decorator(csrf_exempt, name='dispatch')
class TournamentCancelAPI(generics.DestroyAPIView):
    """
    Permet au créateur du tournoi (player_1) d'annuler un tournoi.
    - POST /pong/api/tournaments/<id>/cancel/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.TournamentCancelSerializer
    queryset = Tournament.objects.all()
    lookup_field = 'id'
    
    def perform_destroy(self, instance):
        """Supprime le tournoi et notifie les participants via WebSocket."""
        channel_layer = get_channel_layer()
        if channel_layer is None:
            raise Exception("Configuration WebSocket non disponible")

        # Sauvegarder l'id et le nom avant la suppression
        tournament_id = instance.id
        tournament_name = instance.name
        
        players = [
            instance.player_1,
            instance.player_2,
            instance.player_3,
            instance.player_4
        ]
        players = [p for p in players if p is not None]
        
        # Envoyer les notifications WebSocket
        for player in players:
            group_name = f"user_{player.id}"
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "tournament_cancelled",
                    "tournament_id": tournament_id,
                    "name": tournament_name,
                }
            )

        # Supprimer le tournoi
        instance.delete()
        
        # Conserver les informations pour la réponse
        self.tournament_id = tournament_id
        self.tournament_name = tournament_name
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.perform_destroy(instance)
        
        # Retourner la réponse personnalisée
        return Response({
            "code": 1000,
            "tournament_id": self.tournament_id,
            "name": self.tournament_name,
        })


@method_decorator(csrf_exempt, name='dispatch')
class MatchGetCurrentAPI(generics.GenericAPIView):
    """
    Récupère l'ID d'un tournoi.
    - GET /pong/match/get-id/ : Retourne l'ID du tournoi.
    """
    serializer_class = serializers.MatchGetCurrentSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.to_representation(serializer.validated_data))


@method_decorator(csrf_exempt, name='dispatch')
class TournamentSeeMatchesAPI(generics.GenericAPIView):
    """
    Récupère les matchs en cours d’un tournoi.
    - GET /pong/tournaments/<id>/struct/ : Retourne la liste des matchs en cours du tournoi spécifié.
    """
    serializer_class = serializers.TournamentGetMatchSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    queryset = Tournament.objects.all()

    def get(self, request, *args, **kwargs):
        tournament = self.get_object()
        serializer = self.get_serializer(instance=tournament, context={'request': request})
        return Response(serializer.to_representation(tournament))

def health_check(request):
    return JsonResponse({"status": "ok"})
