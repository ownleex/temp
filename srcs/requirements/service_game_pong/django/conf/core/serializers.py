from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Q
from django.urls import reverse
from rest_framework import generics, permissions, serializers
from core.models import (
    Game,
    Invitation,
    StatusChoices,
    TournamentStatusChoices,
    TypeChoices,
    Winrate,
)
from shared_models.models import Player, Block, Match, Tournament
import os

DOMAIN_NAME = os.getenv("DOMAIN_NAME", "localhost")
PORT_NUM = os.getenv("PORT_NUM", "4343")


class PongPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ["id", "name"]


class PongGameSerializer(serializers.ModelSerializer):
    player_1 = PongPlayerSerializer(read_only=True)
    player_2 = PongPlayerSerializer(read_only=True)
    winner = PongPlayerSerializer(read_only=True)
    url = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = [
            "id",
            "url",
            "round_number",
            "player_1",
            "player_2",
            "score_player_1",
            "score_player_2",
            "status",
            "ball_position",
            "paddle_position",
            "max_score",
            "winner",
        ]

    def get_url(self, obj):
        request = self.context.get("request")
        return reverse("game-detail", args=[obj.match.id, obj.id])


class PongMatchSerializer(serializers.ModelSerializer):
    player_1 = PongPlayerSerializer(read_only=True)
    player_2 = PongPlayerSerializer(read_only=True)
    winner = PongPlayerSerializer(read_only=True)
    games = PongGameSerializer(many=True, read_only=True)
    url = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = [
            "id",
            "url",
            "status",
            "number_of_rounds",
            "type",
            "player_1",
            "player_2",
            "winner",
            "games",
            "tournament",
            "number_of_rounds",
            "created_at",
        ]

    def get_url(self, obj):
        request = self.context.get("request")
        response = {
            "url": reverse("match-detail", args=[obj.id]),
        }
        if (
            request
            and request.user
            and (request.user == obj.player_1.user or request.user == obj.player_2.user)
        ):
            response["ws_url"] = (
                f"wss://{DOMAIN_NAME}:{PORT_NUM}/pong/ws/match/{obj.id}/"
            )
        return response


class PongInvitationSerializer(serializers.ModelSerializer):
    from_player = PongPlayerSerializer(read_only=True)
    to_player = PongPlayerSerializer(read_only=True)
    player_2_id = serializers.IntegerField(write_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Invitation
        fields = [
            "id",
            "from_player",
            "to_player",
            "player_2_id",
            "number_of_rounds",
            "max_score_per_round",
            "match_type",
            "status",
            "created_at",
            "updated_at",
        ]

    def check_player_tournament_and_match_status(self, player, error_code, error_message):
        """
        Vérifie si un joueur est dans un tournoi ouvert ou en cours et s'il a gagné un match.
        Lève une ValidationError si le joueur a gagné un match dans un tournoi ouvert ou en cours.
        """
        # Vérifier les matchs en cours hors tournoi
        if Match.objects.filter(
            Q(player_1=player) | Q(player_2=player),
            status=StatusChoices.EN_COURS,
            tournament__isnull=True
        ).exists():
            raise serializers.ValidationError({
                "code": error_code,
                "message": "Player is already in an ongoing match"
            })

        # Vérifie si le joueur est dans un tournoi ouvert ou en cours
        tournament_query = Tournament.objects.filter(
            Q(player_1=player) | Q(player_2=player) | Q(player_3=player) | Q(player_4=player),
            status__in=[TournamentStatusChoices.EN_COURS]
        )

        if tournament_query.exists():
            # Récupérer les tournois correspondants
            tournaments = tournament_query.values_list('id', flat=True)
            
            # Vérifier si le joueur a gagné un match dans l'un de ces tournois
            if Match.objects.filter(
                tournament__id__in=tournaments,
                winner=player
            ).exists():
                # Si le joueur a gagné un match, lever une erreur
                raise serializers.ValidationError({
                    "code": error_code,
                    "message": error_message
                })

        tournament_inv = Tournament.objects.filter(
            Q(player_1=player) | Q(player_2=player) | Q(player_3=player) | Q(player_4=player),
            status__in=[TournamentStatusChoices.OUVERT]
        )

        if tournament_inv.exists():
            raise serializers.ValidationError({
                "code": error_code,
                "message": "Player is on a prematch"
            })
            # Si le joueur est dans un tournoi mais n'a pas gagné de match, la validation passe

    def validate(self, attrs):
        # Récupérer l'utilisateur connecté et son profil joueur
        user = self.context["request"].user
        try:
            from_player = Player.objects.get(user=user)
        except Player.DoesNotExist:
            raise serializers.ValidationError({"code": 4001, "message": "No player profile"})  # Pas de profil joueur

        # Récupérer les données envoyées
        player_2_id = attrs.get("player_2_id")
        number_of_rounds = 1
        max_score_per_round = attrs.get("max_score_per_round")
        match_type = attrs.get("match_type", TypeChoices.NORMAL)

        # Vérifications des champs requis
        if not player_2_id:
            raise serializers.ValidationError({"code": 4002, "message": "Player ID 2 required"})  # ID du joueur 2 requis

        # Vérifier l'existence du joueur 2
        try:
            to_player = Player.objects.get(id=player_2_id)
        except Player.DoesNotExist:
            raise serializers.ValidationError({"code": 4004, "message": "Player 2 not found"})  # Joueur 2 introuvable

        # Vérifier que les joueurs sont différents
        if from_player == to_player:
            raise serializers.ValidationError({"code": 4005, "message": "Identical players"})  # Joueurs identiques

        # Valider le nombre de manches (si fourni, doit être impair et entre 1 et 5)
        if number_of_rounds is not None:
            try:
                number_of_rounds = int(number_of_rounds)
                if (
                    number_of_rounds < 1
                    or number_of_rounds > 5
                    or number_of_rounds % 2 == 0
                ):
                    raise ValueError
            except (ValueError, TypeError):
                raise serializers.ValidationError(
                    {"code": 4014, "message": "Number of rounds must be odd"}
                )  # Nombre de manches doit être impair
        # Si number_of_rounds n'est pas fourni, le modèle utilisera la valeur par défaut

        # Valider le score maximum par manche (si fourni, doit être impair et positif)
        if max_score_per_round is not None:
            try:
                max_score_per_round = int(max_score_per_round)
                if max_score_per_round < 1 or max_score_per_round % 2 == 0:
                    raise ValueError
            except (ValueError, TypeError):
                raise serializers.ValidationError(
                    {"code": 4013, "message": "Max score must be odd"}
                )  # Score max doit être impair

        # Valider le type de match
        if match_type not in [choice[0] for choice in TypeChoices.choices]:
            raise serializers.ValidationError({"code": 4008, "message": "Invalid match type"})  # Type de match invalide

        # Vérifier si une invitation en attente existe pour to_player
        if Invitation.objects.filter(
            to_player=to_player, status=StatusChoices.EN_ATTENTE
        ).exists():
            raise serializers.ValidationError(
                {"code": 4028, "message": "Existing pending invitation"}
            )  # Invitation en attente existante

        # Vérifier si les joueurs ont gagné un match dans un tournoi ouvert ou en cours
        self.check_player_tournament_and_match_status(
            from_player,
            4009,
            "Player has won a match in an open or ongoing tournament and cannot create a new match"
        )
        self.check_player_tournament_and_match_status(
            to_player,
            4010,
            "Player has won a match in an open or ongoing tournament and cannot create a new match"
        )

        # Vérifier les blocages
        if Block.objects.filter(blocker=to_player, blocked=from_player).exists():
            raise serializers.ValidationError(
                {"code": 4026, "message": "You have blocked this player"}
            )  # Vous avez bloqué ce joueur
        if Block.objects.filter(blocker=from_player, blocked=to_player).exists():
            raise serializers.ValidationError({"code": 4027, "message": "This player has blocked you"})  # Ce joueur vous a bloqué

        # Ajouter les données validées pour la création
        attrs["from_player"] = from_player
        attrs["to_player"] = to_player
        attrs["match_type"] = match_type
        return attrs

    def create(self, validated_data):
        # Supprimer player_2_id des données validées, car il est utilisé pour to_player
        validated_data.pop("player_2_id", None)
        # Définir le statut à EN_ATTENTE
        validated_data["status"] = StatusChoices.EN_ATTENTE
        # Créer l'invitation
        invitation = super().create(validated_data)

        # Envoyer une notification WebSocket au joueur destinataire
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"user_{invitation.to_player.id}",
                {
                    "type": "invitation_received",
                    "invitation_id": invitation.id,
                    "from_player": invitation.from_player.name,
                    "number_of_rounds": invitation.number_of_rounds,
                    "max_score_per_round": invitation.max_score_per_round,
                    "match_type": invitation.match_type,
                },
            )

        return invitation


class InvitationCancelSerializer(serializers.Serializer):
    def validate(self, attrs):
        invitation = self.instance
        user = self.context["request"].user

        # Vérifier si l'utilisateur a un profil joueur
        try:
            player = Player.objects.get(user=user)
        except Player.DoesNotExist:
            raise serializers.ValidationError({"code": 4001, "message": "No player profile"})  # Pas de profil joueur

        # Vérifier si le joueur est l'expéditeur de l'invitation
        if invitation.from_player != player:
            raise serializers.ValidationError({"code": 4029, "message": "Not the sender"})  # Pas l'expéditeur

        # Vérifier si l'invitation est en attente
        if invitation.status != StatusChoices.EN_ATTENTE:
            raise serializers.ValidationError(
                {"code": 4011, "message": "Invitation not pending"}
            )  # Invitation non en attente

        attrs["player"] = player
        return attrs

    def update(self, instance, validated_data):
        # Mettre à jour l'invitation
        instance.status = StatusChoices.ANNULEE
        instance.save()

        # Notifier le joueur destinataire via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{instance.to_player.id}",
            {
                "type": "invitation_canceled",
                "invitation_id": instance.id,
                "from_player": instance.from_player.name,
            },
        )

        return instance

    def to_representation(self, instance):
        return {
            "code": 1000,
            "invitation_id": instance.id,
        }


class InvitationAcceptSerializer(serializers.Serializer):
    def check_player_tournament_and_match_status(self, player, error_code, error_message):
        """
        Vérifie si un joueur est dans un tournoi ouvert ou en cours et s'il a gagné un match,
        ou s'il est dans un match en cours hors tournoi.
        """
        if Match.objects.filter(
            Q(player_1=player) | Q(player_2=player),
            status=StatusChoices.EN_COURS,
            tournament__isnull=True
        ).exists():
            raise serializers.ValidationError({
                "code": error_code,
                "message": "Player is already in an ongoing match"
            })

        tournament_query = Tournament.objects.filter(
            Q(player_1=player) | Q(player_2=player) | Q(player_3=player) | Q(player_4=player),
            status__in=[TournamentStatusChoices.OUVERT, TournamentStatusChoices.EN_COURS]
        )

        if tournament_query.exists():
            tournaments = tournament_query.values_list('id', flat=True)
            if Match.objects.filter(
                tournament__id__in=tournaments,
                winner=player
            ).exists():
                raise serializers.ValidationError({
                    "code": error_code,
                    "message": error_message
                })

        tournament_inv = Tournament.objects.filter(
        Q(player_1=player) | Q(player_2=player) | Q(player_3=player) | Q(player_4=player),
        status__in=[TournamentStatusChoices.OUVERT]
        )

        if tournament_inv.exists():
            raise serializers.ValidationError({
                "code": error_code,
                "message": "Player is on a prematch"
            })

    def validate(self, attrs):
        invitation = self.instance
        user = self.context["request"].user

        try:
            player = Player.objects.get(user=user)
        except Player.DoesNotExist:
            raise serializers.ValidationError({"code": 4001, "message": "No player profile"})

        if invitation.to_player != player:
            raise serializers.ValidationError({"code": 4010, "message": "Not the recipient"})

        if invitation.status != StatusChoices.EN_ATTENTE:
            raise serializers.ValidationError({"code": 4011, "message": "Invitation not pending"})

        self.check_player_tournament_and_match_status(
            invitation.from_player,
            4009,
            "Sender has won a match in an open or ongoing tournament and cannot play a new match"
        )
        self.check_player_tournament_and_match_status(
            invitation.to_player,
            4010,
            "Recipient has won a match in an open or ongoing tournament and cannot play a new match"
        )

        attrs["player"] = player
        return attrs

    def update(self, instance, validated_data):
        instance.status = StatusChoices.ACCEPTEE
        instance.save()

        match = Match.objects.create(
            player_1=instance.from_player,
            player_2=instance.to_player,
            number_of_rounds=instance.number_of_rounds,
            status=StatusChoices.EN_COURS,
            type=instance.match_type,
        )

        game = Game.objects.create(
            match=match,
            player_1=match.player_1,
            player_2=match.player_2,
            status=StatusChoices.EN_COURS,
            ball_position={"x": 35.5, "y": 15.5},
            paddle_position={"paddle_l": 15, "paddle_r": 15},
            round_number=1,
            max_score=instance.max_score_per_round,
        )
        game.initialize_ball_direction()
        game.save()

        other_invitations = Invitation.objects.filter(
            from_player=instance.from_player, status=StatusChoices.EN_ATTENTE
        ).exclude(id=instance.id)
        for inv in other_invitations:
            inv.status = StatusChoices.ANNULEE
            inv.save()

        channel_layer = get_channel_layer()
        for player_id in [instance.from_player.id, instance.to_player.id]:
            async_to_sync(channel_layer.group_send)(
                f"user_{player_id}",
                {
                    "type": "match_created",
                    "match_id": match.id,
                    "player_1": match.player_1.name,
                    "player_2": match.player_2.name,
                    "number_of_rounds": match.number_of_rounds,
                    "match_type": match.type,
                },
            )

        return instance

    def to_representation(self, instance):
        return {
            "code": 1000,
            "match_id": Match.objects.get(
                player_1=instance.from_player,
                player_2=instance.to_player,
                status=StatusChoices.EN_COURS,
            ).id,
        }


class InvitationDeclineSerializer(serializers.Serializer):
    def validate(self, attrs):
        invitation = self.instance
        user = self.context["request"].user

        # Vérifier si l'utilisateur a un profil joueur
        try:
            player = Player.objects.get(user=user)
        except Player.DoesNotExist:
            raise serializers.ValidationError({"code": 4001, "message": "No player profile"})  # Pas de profil joueur

        # Vérifier si le joueur est le destinitaire de l'invitation
        if invitation.to_player != player:
            raise serializers.ValidationError({"code": 4010, "message": "Not the recipient"})  # Pas le destinataire

        # Vérifier si l'invitation est en attente
        if invitation.status != StatusChoices.EN_ATTENTE:
            raise serializers.ValidationError(
                {"code": 4011, "message": "Invitation not pending"}
            )  # Invitation non en attente

        attrs["player"] = player
        return attrs

    def update(self, instance, validated_data):
        # Mettre à jour l'invitation
        instance.status = StatusChoices.REFUSEE
        instance.save()

        # Notifier le joueur initiateur via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{instance.from_player.id}",
            {
                "type": "invitation_declined",
                "invitation_id": instance.id,
                "to_player": instance.to_player.name,
            },
        )

        return instance

    def to_representation(self, instance):
        return {
            "code": 1000,
            "invitation_id": instance.id,
        }


# -----------------------------------------------------------------#


class TournamentCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50, required=False)
    max_score_per_round = serializers.IntegerField(default=3, min_value=1, max_value=9)

    def check_player_tournament_and_match_status(self, player, error_code, error_message):
        """
        Vérifie si un joueur est dans un tournoi ouvert ou en cours et s'il a gagné un match,
        ou s'il est dans un match en cours hors tournoi.
        """
        if Match.objects.filter(
            Q(player_1=player) | Q(player_2=player),
            status=StatusChoices.EN_COURS,
            tournament__isnull=True
        ).exists():
            raise serializers.ValidationError({
                "code": error_code,
                "message": "Player is already in an ongoing match"
            })

        tournament_query = Tournament.objects.filter(
            Q(player_1=player) | Q(player_2=player) | Q(player_3=player) | Q(player_4=player),
            status__in=[TournamentStatusChoices.OUVERT, TournamentStatusChoices.EN_COURS]
        )

        if tournament_query.exists():
            tournaments = tournament_query.values_list('id', flat=True)
            if Match.objects.filter(
                tournament__id__in=tournaments,
                winner=player
            ).exists():
                raise serializers.ValidationError({
                    "code": error_code,
                    "message": error_message
                })

    def validate(self, attrs):
        user = self.context["request"].user
        try:
            player = Player.objects.get(user=user)
        except Player.DoesNotExist:
            raise serializers.ValidationError({"code": 4001, "message": "No player profile associated with the user"})

        self.check_player_tournament_and_match_status(
            player,
            4009,
            "Player has won a match in an open or ongoing tournament and cannot create a new tournament"
        )
        
        invite_query = Invitation.objects.filter(from_player=player, status=StatusChoices.EN_ATTENTE)
        if invite_query.exists():
            raise serializers.ValidationError({"code": 4009, "message": "Player on a prematch"})

        if attrs["max_score_per_round"] % 2 == 0:
            raise serializers.ValidationError({"code": 4013, "message": "The maximum score per round must be odd"})

        attrs["player_1"] = player
        return attrs

    def create(self, validated_data):
        tournament = Tournament.objects.create(
            player_1=validated_data["player_1"],
            name=validated_data.get("name", ""),
            max_score_per_round=validated_data["max_score_per_round"],
            number_of_rounds=1,
        )
        return tournament

    def to_representation(self, instance):
        return {
            "code": 1000,
            "tournament_id": instance.id,
            "name": instance.name,
            "status": instance.status,
        }


class TournamentListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tournament
        fields = [
            "id",
            "name",
            "player_1",
            "player_2",
            "player_3",
            "player_4",
            "status",
            "winner",
            "max_score_per_round",
            "number_of_rounds",
            "created_at",
        ]


class TournamentMatchSerializer(serializers.ModelSerializer):
    player_1 = PongPlayerSerializer(read_only=True)
    player_2 = PongPlayerSerializer(read_only=True)
    winner = PongPlayerSerializer(read_only=True)

    class Meta:
        model = Match
        fields = [
            "id",
            "tournament",
            "player_1",
            "player_2",
            "number_of_rounds",
            "winner",
            "created_at",
            "updated_at",
        ]


class TournamentJoinSerializer(serializers.Serializer):
    def check_player_tournament_and_match_status(self, player, error_code, error_message):
        """
        Vérifie si un joueur est dans un tournoi ouvert ou en cours et s'il a gagné un match,
        ou s'il est dans un match en cours hors tournoi.
        """
        if Match.objects.filter(
            Q(player_1=player) | Q(player_2=player),
            status=StatusChoices.EN_COURS,
            tournament__isnull=True
        ).exists():
            raise serializers.ValidationError({
                "code": error_code,
                "message": "Player is already in an ongoing match"
            })

        tournament_query = Tournament.objects.filter(
            Q(player_1=player) | Q(player_2=player) | Q(player_3=player) | Q(player_4=player),
            status__in=[TournamentStatusChoices.OUVERT, TournamentStatusChoices.EN_COURS]
        )

        if tournament_query.exists():
            tournaments = tournament_query.values_list('id', flat=True)
            if Match.objects.filter(
                tournament__id__in=tournaments,
                winner=player
            ).exists():
                raise serializers.ValidationError({
                    "code": error_code,
                    "message": error_message
                })

    def validate(self, attrs):
        tournament = self.instance
        user = self.context["request"].user

        try:
            player = Player.objects.get(user=user)
        except Player.DoesNotExist:
            raise serializers.ValidationError({"code": 4001, "message": "No player profile associated with the user"})

        self.check_player_tournament_and_match_status(
            player,
            4009,
            "Player has won a match in an open or ongoing tournament and cannot join a new tournament"
        )

        invite_query = Invitation.objects.filter(from_player=player, status=StatusChoices.EN_ATTENTE)
        if invite_query.exists():
            raise serializers.ValidationError({"code": 4009, "message": "Player on a prematch"})


        if all([tournament.player_1, tournament.player_2, tournament.player_3, tournament.player_4]):
            raise serializers.ValidationError({"code": 4015, "message": "Full tournament"})

        if tournament.status != TournamentStatusChoices.OUVERT:
            raise serializers.ValidationError({"code": 4016, "message": "Tournament not open"})

        attrs["player"] = player
        return attrs

    def update(self, instance, validated_data):
        player = validated_data["player"]
        channel_layer = get_channel_layer()

        current_players = [
            instance.player_1,
            instance.player_2,
            instance.player_3,
            instance.player_4,
        ]
        current_players = [p for p in current_players if p is not None]

        if instance.player_2 is None:
            instance.player_2 = player
        elif instance.player_3 is None:
            instance.player_3 = player
        elif instance.player_4 is None:
            instance.player_4 = player

        players_to_notify = current_players + [player]
        for p in players_to_notify:
            async_to_sync(channel_layer.group_send)(
                f"user_{p.id}",
                {
                    "type": "player_joined",
                    "tournament_id": instance.id,
                    "name": instance.name,
                    "joined_player": player.name,
                },
            )

        if instance.player_4 is not None:
            async_to_sync(channel_layer.group_send)(
                f"user_{instance.player_1.id}",
                {
                    "type": "tournament_ready",
                    "tournament_id": instance.id,
                    "name": instance.name,
                },
            )

        instance.save()
        return instance

    def to_representation(self, instance):
        return {"code": 1000, "tournament_id": instance.id, "name": instance.name}


class TournamentStartSerializer(serializers.Serializer):
    def validate(self, attrs):
        tournament = self.instance
        user = self.context["request"].user

        # Vérifier que l'utilisateur a un profil joueur
        try:
            player = Player.objects.get(user=user)
        except Player.DoesNotExist:
            raise serializers.ValidationError(
                {"code": 4001, "message": "No player profile associated with the user"}
            )  # Aucun profil joueur associé à l'utilisateur

        # Vérifier que l'utilisateur est le créateur du tournoi (player_1)
        if tournament.player_1.user != user:
            raise serializers.ValidationError(
                {"code": 4012, "message": "User not authorized to start this tournament"}
            )  # Utilisateur non autorisé à démarrer ce tournoi

        # Vérifier que le tournoi est en statut OUVERT
        if tournament.status != TournamentStatusChoices.OUVERT:
            raise serializers.ValidationError({"code": 4016, "message": "Tournament not open"})  # Tournoi non ouvert

        # Vérifier qu'il y a exactement 4 joueurs
        players = [
            tournament.player_1,
            tournament.player_2,
            tournament.player_3,
            tournament.player_4,
        ]
        players = [p for p in players if p is not None]
        if len(players) != 4:
            raise serializers.ValidationError(
                {"code": 4015, "message": "Tournament must have exactly 4 players"}
            )  # Tournoi doit avoir exactement 4 joueurs

        return attrs

    def calculate_win_rate(self, player):
        """Calcule le winrate d'un joueur."""
        try:
            # Récupérer ou créer le winrate si nécessaire
            winrate, _ = Winrate.objects.get_or_create(player=player)
            total_games = winrate.victory + winrate.defeat
            if total_games == 0:
                return 0.0
            return (winrate.victory / total_games) * 100
        except Exception:
            # En cas d'erreur, retourner 0
            return 0.0

    def pair_players(self, tournament):
        """Trie les joueurs par win rate et crée les paires pour les demi-finales."""
        players = [
            tournament.player_1,
            tournament.player_2,
            tournament.player_3,
            tournament.player_4,
        ]
        players = [p for p in players if p is not None]

        # Trier les joueurs par win rate (du plus fort au plus faible)
        sorted_players = sorted(players, key=self.calculate_win_rate, reverse=True)

        # Créer les paires : 1er vs 4ème, 2ème vs 3ème
        return [
            (sorted_players[0], sorted_players[3]),  # Meilleur vs Pire
            (
                sorted_players[1],
                sorted_players[2],
            ),  # Deuxième meilleur vs Deuxième pire
        ]

    def update(self, instance, validated_data):
        """Démarre le tournoi en créant les matchs et mettant à jour le statut."""
        channel_layer = get_channel_layer()

        # Notifier tous les participants que le tournoi a commencé
        players = [
            instance.player_1,
            instance.player_2,
            instance.player_3,
            instance.player_4,
        ]
        for player in players:
            group_name = f"user_{player.id}"
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "tournament_started",
                    "tournament_id": instance.id,
                    "name": instance.name,
                },
            )

        # Récupérer les paires de joueurs
        pairs = self.pair_players(instance)

        # Créer les deux matchs (demi-finales) et notifier les joueurs
        for i, (player_1, player_2) in enumerate(pairs, 1):
            match = Match.objects.create(
                tournament=instance,
                player_1=player_1,
                player_2=player_2,
                number_of_rounds=1,
                match_number=2,
                status=StatusChoices.EN_COURS,
                type=TypeChoices.TOURNAMENT,
            )
            game = Game.objects.create(
                match=match,
                player_1=match.player_1,
                player_2=match.player_2,
                ball_position={"x": 35.5, "y": 15.5},
                paddle_position={"paddle_l": 15, "paddle_r": 15},
                status=StatusChoices.EN_COURS,
                round_number=1,
                max_score=instance.max_score_per_round,
            )
            game.save()
            # Notifier les deux joueurs du match
            for player in [player_1, player_2]:
                group_name = f"user_{player.id}"
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        "type": "match_created",
                        "match_id": match.id,
                        "player_1": match.player_1.name,
                        "player_2": match.player_2.name,
                        "number_of_rounds": instance.number_of_rounds,
                        "max_score_per_round": instance.max_score_per_round,
                        "match_type": "tournament_semi_final",
                        "ws_url": f"wss://{DOMAIN_NAME}:{PORT_NUM}/pong/ws/match/{match.id}/",
                        "tournament_id": instance.id,
                        "tournament_name": instance.name,
                    },
                )

        # Mettre à jour le statut du tournoi
        instance.status = TournamentStatusChoices.EN_COURS
        instance.save()

        return instance

    def to_representation(self, instance):
        return {
            "code": 1000,
            "tournament_id": instance.id,
            "name": instance.name,
            "status": instance.status,
        }


class TournamentStartFinalSerializer(serializers.Serializer):
    def validate(self, attrs):
        tournament = self.instance
        user = self.context["request"].user

        # Vérifier que l'utilisateur a un profil joueur
        try:
            player = Player.objects.get(user=user)
        except Player.DoesNotExist:
            raise serializers.ValidationError(
                {"code": 4001, "message": "No player profile associated with the user"}
            )  # Aucun profil joueur associé à l'utilisateur

        # Vérifier que le joueur est présent dans le tournoi
        if player not in [
            tournament.player_1,
            tournament.player_2,
            tournament.player_3,
            tournament.player_4,
        ]:
            raise serializers.ValidationError(
                {"code": 4017, "message": "Only one participant of the tournament can start the final"}
            )  # Seul un participant du tournoi peut démarrer la finale

        # Vérifier que le tournoi est en statut EN_COURS
        if tournament.status != TournamentStatusChoices.EN_COURS:
            raise serializers.ValidationError(
                {"code": 4018, "message": "Tournament must be underway to start the final"}
            )  # Tournoi doit être en cours pour lancer la finale

        # Vérifier que les demi-finales sont terminées
        demi_finales = Match.objects.filter(match_number=2, tournament=tournament)
        if demi_finales.count() != 2:
            raise serializers.ValidationError(
                {"code": 4022, "message": "Tournament must have exactly two semi-final matches"}
            )  # Tournoi doit avoir exactement deux matchs de demi-finales
        for match in demi_finales:
            if match.status != StatusChoices.TERMINE:
                raise serializers.ValidationError(
                    {"code": 4023, "message": "All semi-final matches must be completed"}
                )  # Tous les matchs des demi-finales doivent être terminés
            if not match.winner:
                raise serializers.ValidationError(
                    {"code": 4024, "message": "Tous les matchs des demi-finales doivent avoir un gagnant"}
                )  # Tous les matchs des demi-finales doivent avoir un gagnant

        # Vérifier qu'il n'y a pas déjà une finale
        if Match.objects.filter(match_number=1, tournament=tournament).exists():
            raise serializers.ValidationError(
                {"code": 4025, "message": "The final has already been created"}
            )  # La finale a déjà été créée

        return attrs

    def update(self, instance, validated_data):
        # Récupérer les gagnants des demi-finales
        demi_finales = Match.objects.filter(match_number=2, tournament=instance)
        finalists = [match.winner for match in demi_finales]

        # Créer le match de la finale
        final_match = Match.objects.create(
            tournament=instance,
            match_number=1,
            player_1=finalists[0],
            player_2=finalists[1],
            number_of_rounds=1,
            status=StatusChoices.EN_COURS,
            type=TypeChoices.TOURNAMENT,
        )

        game = Game.objects.create(
            match=final_match,
            player_1=final_match.player_1,
            player_2=final_match.player_2,
            ball_position={"x": 35.5, "y": 15.5},
            paddle_position={"paddle_l": 15, "paddle_r": 15},
            status=StatusChoices.EN_COURS,
            round_number=1,
            max_score=instance.max_score_per_round,
        )
        game.save()

        # Envoyer une notification WebSocket aux finalistes
        channel_layer = get_channel_layer()
        for player in finalists:
            group_name = f"user_{player.id}"
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "match_created",
                    "match_id": final_match.id,
                    "player_1": final_match.player_1.name,
                    "player_2": final_match.player_2.name,
                    "number_of_rounds": instance.number_of_rounds,
                    "max_score_per_round": instance.max_score_per_round,
                    "match_type": "tournament_final",
                    "ws_url": f"wss://{DOMAIN_NAME}:{PORT_NUM}/pong/ws/match/{final_match.id}/",
                },
            )

        return instance

    def to_representation(self, instance):
        return {
            "code": 1000,
            "tournament_id": instance.id,
            "name": instance.name,
            "status": instance.status,
        }


class TournamentEndSerializer(serializers.Serializer):
    def validate(self, attrs):
        tournament = self.instance
        user = self.context["request"].user

        # Vérifier que l'utilisateur a un profil joueur
        try:
            player = Player.objects.get(user=user)
        except Player.DoesNotExist:
            raise serializers.ValidationError(
                {"code": 4001, "message": "No player profile associated with the user"}
            )  # Aucun profil joueur associé à l'utilisateur

        # Vérifier que le joueur est présent dans le tournoi
        if player not in [
            tournament.player_1,
            tournament.player_2,
            tournament.player_3,
            tournament.player_4,
        ]:
            raise serializers.ValidationError(
                {"code": 4017, "message": "Only one tournament participant can complete the tournament"}
            )  # Seul un participant du tournoi peut terminer le tournoi

        # Vérifier que le tournoi est en statut EN_COURS
        if tournament.status != TournamentStatusChoices.EN_COURS:
            raise serializers.ValidationError(
                {"code": 4018, "message": "The tournament must be in progress to be completed"}
            )  # Tournoi doit être en cours pour être terminé

        # Vérifier que les matchs sont terminés
        matchs = Match.objects.filter(
            Q(match_number=2) | Q(match_number=3), tournament=tournament
        )
        if matchs.count() != 3:
            raise serializers.ValidationError(
                {"code": 4019, "message": "Tournament must have exactly three matches"}
            )  # Tournoi doit avoir exactement trois matchs
        for match in matchs:
            if match.status != StatusChoices.TERMINE:
                raise serializers.ValidationError(
                    {"code": 4020, "message": "All matches must be completed"}
                )  # Tous les matchs doivent être terminés
            if not match.winner:
                raise serializers.ValidationError(
                    {"code": 4021, "message": "Every match must have a winner"}
                )  # Tous les matchs doivent avoir un gagnant

        return attrs

    def update(self, instance, validated_data):
        # Mettre à jour le statut du tournoi
        instance.status = TournamentStatusChoices.TERMINE
        instance.save()
        return instance

    def to_representation(self, instance):
        return {
            "code": 1000,
            "tournament_id": instance.id,
            "name": instance.name,
            "status": instance.status,
        }


class TournamentLeaveSerializer(serializers.Serializer):
    def validate(self, attrs):
        tournament = self.instance
        user = self.context["request"].user

        # Vérifier si l'utilisateur a un profil joueur
        try:
            player = Player.objects.get(user=user)
        except Player.DoesNotExist:
            raise serializers.ValidationError(
                {"code": 4001, "message": "No player profile associated with the user"}
            )  # Aucun profil joueur associé à l'utilisateur

        # Vérifier si le joueur fait partie du tournoi
        if player not in [
            tournament.player_1,
            tournament.player_2,
            tournament.player_3,
            tournament.player_4,
        ]:
            raise serializers.ValidationError(
                {"code": 4031, "message": "You are not part of this tournament"}
            )  # Vous ne faites pas partie de ce tournoi

        # Vérifier que le joueur n'est pas player_1
        if player == tournament.player_1:
            raise serializers.ValidationError(
                {"code": 4032, "message": "Player 1 cannot leave the tournament"}
            )  # Le joueur 1 ne peut pas quitter le tournoi

        # Vérifier si le joueur est déjà dans un autre tournoi ouvert ou en cours
        if (
            Tournament.objects.filter(
                Q(player_1=player)
                | Q(player_2=player)
                | Q(player_3=player)
                | Q(player_4=player),
                Q(status=TournamentStatusChoices.OUVERT)
                | Q(status=TournamentStatusChoices.EN_COURS),
            )
            .exclude(id=tournament.id)
            .exists()
        ):
            raise serializers.ValidationError(
                {"code": 4009, "message": "Player already in an open or ongoing tournament"}
            )  # Joueur déjà dans un tournoi ouvert ou en cours

        # Vérifier si le tournoi est ouvert
        if tournament.status != TournamentStatusChoices.OUVERT:
            raise serializers.ValidationError({"code": 4016, "message": "Tournament has already started"})  # Tournoi a déjà démarré

        attrs["player"] = player
        return attrs

    def update(self, instance, validated_data):
        player = validated_data["player"]
        channel_layer = get_channel_layer()

        # Liste des joueurs actuels (non nuls) avant de retirer le joueur
        current_players = [
            instance.player_1,
            instance.player_2,
            instance.player_3,
            instance.player_4,
        ]
        current_players = [p for p in current_players if p is not None]

        # Retirer le joueur
        if instance.player_2 == player:
            instance.player_2 = None
        elif instance.player_3 == player:
            instance.player_3 = None
        elif instance.player_4 == player:
            instance.player_4 = None

        # Notifier tous les joueurs actuels (y compris le joueur qui quitte)
        players_to_notify = current_players
        for p in players_to_notify:
            group_name = f"user_{p.id}"
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "player_leave",
                    "tournament_id": instance.id,
                    "name": instance.name,
                    "leaved_player": player.name,
                },
            )
        instance.save()
        return instance

    def to_representation(self, instance):
        return {"code": 1000, "tournament_id": instance.id, "name": instance.name}


class TournamentSeeFinalSerializer(serializers.Serializer):
    def validate(self, attrs):
        tournament = self.instance
        user = self.context["request"].user

        # Vérifier que l'utilisateur a un profil joueur
        try:
            player = Player.objects.get(user=user)
        except Player.DoesNotExist:
            raise serializers.ValidationError(
                {"code": 4001, "message": "No player profile associated with the user"}
            )  # Aucun profil joueur associé à l'utilisateur

        # Vérifier que le joueur est présent dans le tournoi
        if player not in [
            tournament.player_1,
            tournament.player_2,
            tournament.player_3,
            tournament.player_4,
        ]:
            raise serializers.ValidationError(
                {"code": 4017, "message": "Only one participant of the tournament can start the final"}
            )  # Seul un participant du tournoi peut démarrer la finale

        # Vérifier que le tournoi est en statut EN_COURS
        if tournament.status != TournamentStatusChoices.EN_COURS:
            raise serializers.ValidationError(
                {"code": 4018, "message": "Tournament must be underway to start the final"}
            )  # Tournoi doit être en cours pour lancer la finale

        # Vérifier que les demi-finales sont terminées
        demi_finales = Match.objects.filter(match_number=2, tournament=tournament)
        if demi_finales.count() != 2:
            raise serializers.ValidationError(
                {"code": 4022, "message": "Tournament must have exactly two semi-final matches"}
            )  # Tournoi doit avoir exactement deux matchs de demi-finales
        for match in demi_finales:
            if match.status != StatusChoices.TERMINE:
                raise serializers.ValidationError(
                    {"code": 4023, "message": "All semi-final matches must be completed"}
                )  # Tous les matchs des demi-finales doivent être terminés
            if not match.winner:
                raise serializers.ValidationError(
                    {"code": 4024, "message": "All semi-final matches must have a winner"}
                )  # Tous les matchs des demi-finales doivent avoir un gagnant

        finalists = [match.winner for match in demi_finales]
        attrs["finalist1"] = finalists[0]
        attrs["finalist2"] = finalists[1]
        return attrs

    def to_representation(self, instance):
        validated_data = self.validated_data
        finalist1 = validated_data["finalist1"]
        finalist2 = validated_data["finalist2"]
        return {
            "code": 1000,
            "finalist1": finalist1.username if finalist1 else None,  # Nom du joueur
            "finalist2": finalist2.username if finalist2 else None,  # Nom du joueur
        }


class TournamentGetMatchSerializer(serializers.Serializer):
    def validate(self, attrs):
        tournament = self.instance
        user = self.context["request"].user

        # Vérifier que l'utilisateur a un profil joueur
        try:
            player = Player.objects.get(user=user)
        except Player.DoesNotExist:
            raise serializers.ValidationError(
                {"code": 4001, "message": "No player profile associated with the user"}
            )  # Aucun profil joueur associé à l'utilisateur

        # Vérifier que le joueur est présent dans le tournoi
        if player not in [
            tournament.player_1,
            tournament.player_2,
            tournament.player_3,
            tournament.player_4,
        ]:
            raise serializers.ValidationError(
                {"code": 4017, "message": "Only one tournament participant can access the matches"}
            )  # Seul un participant du tournoi peut accéder aux matchs

        return attrs

    def to_representation(self, instance):
        tournament = self.instance
        # Récupérer les matchs en cours pour ce tournoi
        matches_en_cours = Match.objects.filter(
            tournament=tournament,
        )

        # Préparer la liste des matchs pour la réponse
        matches_data = [
            {
                "match_id": match.id,
                "match_number": match.match_number,
                "player_1": match.player_1.name if match.player_1 else None,
                "player_2": match.player_2.name if match.player_2 else None,
                "type": match.type,
                "created_at": match.created_at,
            }
            for match in matches_en_cours
        ]

        return {"code": 1000, "matches": matches_data}


class TournamentCancelSerializer(serializers.Serializer):
    def validate(self, attrs):
        tournament = self.instance
        user = self.context["request"].user

        # Vérifier que l'utilisateur a un profil joueur
        try:
            player = Player.objects.get(user=user)
        except Player.DoesNotExist:
            raise serializers.ValidationError(
                {"code": 4001, "message": "No associated player profile"}
            )  # Aucun profil joueur associé

        # Vérifier que le joueur est le créateur du tournoi
        if player != tournament.player_1:
            raise serializers.ValidationError(
                {"code": 4012, "message": "Not allowed to delete this tournament"}
            )  # Non autorisé à supprimer ce tournoi

        # Vérifier que le tournoi est en statut OUVERT
        if tournament.status != TournamentStatusChoices.OUVERT:
            raise serializers.ValidationError(
                {"code": 4028, "message": "Non-deletable tournament (not in open status)"}
            )  # Tournoi non supprimable (pas en statut ouvert)

        return attrs


class TournamentGetIdSerializer(serializers.Serializer):
    def validate(self, attrs):
        user = self.context["request"].user

        # Vérifier si l'utilisateur a un profil joueur
        try:
            player = Player.objects.get(user=user)
        except Player.DoesNotExist:
            raise serializers.ValidationError(
                {"code": 4001, "message": "No associated player profile"}
            )  # Aucun profil joueur associé

        # Vérifier si le joueur participe à un tournoi ouvert ou en cours
        tournament = Tournament.objects.filter(
            Q(player_1=player)
            | Q(player_2=player)
            | Q(player_3=player)
            | Q(player_4=player),
            status__in=[
                TournamentStatusChoices.OUVERT,
                TournamentStatusChoices.EN_COURS,
            ],
        ).first()

        # Gestion des finalistes
        demi_finales = Match.objects.filter(match_number=2, tournament=tournament)
        finalists = [match.winner for match in demi_finales if match.winner]
        if len(finalists) < 2:
            attrs["finalist1"] = finalists[0] if len(finalists) > 0 else None
            attrs["finalist2"] = finalists[1] if len(finalists) > 1 else None
        else:
            attrs["finalist1"] = finalists[0]
            attrs["finalist2"] = finalists[1]

        attrs["player"] = player
        attrs["tournament"] = tournament
        return attrs

    def to_representation(self, validated_data):
        tournament = validated_data["tournament"]
        finalist1 = validated_data["finalist1"]
        finalist2 = validated_data["finalist2"]
        return {
            "code": 1000,
            "tournament_id": tournament.id if tournament else None,
            "name": tournament.name if tournament else None,
            "status": tournament.status if tournament else None,
            "finalist1": finalist1.name if finalist1 else None,
            "finalist2": finalist2.name if finalist2 else None,
        }


class WinrateSerializer(serializers.ModelSerializer):
    player = PongPlayerSerializer(read_only=True)

    class Meta:
        model = Winrate
        fields = ["id", "player", "victory", "defeat"]


class MatchGetCurrentSerializer(serializers.Serializer):
    def validate(self, attrs):
        user = self.context["request"].user

        # Vérifier si l'utilisateur a un profil joueur
        try:
            player = Player.objects.get(user=user)
        except Player.DoesNotExist:
            raise serializers.ValidationError(
                {"code": 4001, "message": "No associated player profile"}
            )  # Aucun profil joueur associé

        # Récupérer le match en cours pour ce joueur
        match = Match.objects.filter(
            Q(player_1=player) | Q(player_2=player), status__in=[StatusChoices.EN_COURS]
        ).first()
        attrs["match"] = match

        return attrs

    def to_representation(self, validated_data):
        match = validated_data["match"]
        return {
            "code": 1000,
            "match_id": match.id if match else None,
            "ws_url": (
                f"wss://{DOMAIN_NAME}:{PORT_NUM}/pong/ws/match/{match.id}/"
                if match
                else None
            ),
            "player_1": match.player_1.name if match else None,
            "player_2": match.player_2.name if match else None,
        }
