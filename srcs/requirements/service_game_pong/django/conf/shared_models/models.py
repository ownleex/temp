from django.db import models
from django.contrib.auth.models import User
import uuid
import random


class StatusChoices(models.TextChoices):
    EN_ATTENTE = "En attente"
    ACCEPTEE = "Acceptée"
    REFUSEE = "Refusée"
    EN_COURS = "En cours"
    TERMINE = "Terminée"
    ANNULEE = "Annulée"


class TypeChoices(models.TextChoices):
    IA = "IA"
    NORMAL = "Normal"
    TOURNAMENT = "Tournois"


class TournamentStatusChoices(models.TextChoices):
    OUVERT = "Ouvert"
    EN_COURS = "En cours"
    TERMINE = "Terminée"


class Player(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="player_profile",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    forty_two_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    name = models.CharField(max_length=20)
    online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)
    description = models.TextField(max_length=20, blank=True, default="")
    avatar = models.ImageField(
        upload_to="avatars/", null=True, blank=True, default="avatars/default.jpg"
    )
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_method = models.CharField(
        max_length=10, choices=[("TOTP", "TOTP")], default="TOTP", blank=True
    )  # Méthode de 2FA

    friends = models.ManyToManyField(
        "self", symmetrical=False, through="Friendship", related_name="friends_of"
    )

    def __str__(self):
        return self.name


class Friendship(models.Model):
    player_1 = models.ForeignKey(
        Player,
        related_name="friendship_requests",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    player_2 = models.ForeignKey(
        Player,
        related_name="friendships",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        choices=[
            ("pending", "Pending"),
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
        ],
        default="pending",
        max_length=10,
    )

    class Meta:
        unique_together = ("player_1", "player_2")

    def __str__(self):
        return f"{self.player_1.name} - {self.player_2.name} ({self.status})"


class Block(models.Model):
    blocker = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="blocked_by"
    )  # Celui qui bloque
    blocked = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="blocked_players"
    )  # Celui qui est bloqué
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            "blocker",
            "blocked",
        ]  # Un joueur ne peut bloquer un autre joueur qu'une seule fois

    def __str__(self):
        return f"{self.blocker.name} blocked {self.blocked.name}"


class Tournament(models.Model):
    name = models.CharField(max_length=30, blank=True)
    player_1 = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="player1_tournament", null=True
    )
    player_2 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="player2_tournament",
        null=True,
        blank=True,
    )
    player_3 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="player3_tournament",
        null=True,
        blank=True,
    )
    player_4 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="player4_tournament",
        null=True,
        blank=True,
    )
    status = models.CharField(
        choices=TournamentStatusChoices.choices,
        max_length=20,
        default=TournamentStatusChoices.OUVERT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    winner = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="won_tournaments",
    )
    max_score_per_round = models.PositiveIntegerField(default=3)
    number_of_rounds = models.PositiveIntegerField(default=3)

    def save(self, *args, **kwargs):
        if not self.name and self.player_1:
            self.name = f"Tournoi de {self.player_1.name}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.status})"


class Match(models.Model):
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name="tournament",
        null=True,
        blank=True,
    )
    match_number = models.PositiveIntegerField(
        default=0, null=True, blank=True
    )  # final = 1, demi-final=2
    player_1 = models.ForeignKey(
        Player, on_delete=models.SET_NULL, related_name="matches_as_player_1", null=True
    )
    player_2 = models.ForeignKey(
        Player, on_delete=models.SET_NULL, related_name="matches_as_player_2", null=True
    )
    status = models.CharField(
        choices=StatusChoices.choices, max_length=10, default=StatusChoices.EN_COURS
    )
    number_of_rounds = models.PositiveIntegerField(default=1)
    max_score_per_round = models.PositiveIntegerField(default=3)
    type = models.CharField(
        choices=TypeChoices.choices, max_length=10, default=TypeChoices.NORMAL
    )
    winner = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        related_name="won_matches",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Match {self.id} - {self.status} - {self.type}"
