from django.contrib import admin
from shared_models.models import Player, Friendship, Block, Match, Tournament
from .models import Invitation, Game, Winrate


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'online')

class FriendshipAdmin(admin.ModelAdmin):
    list_display = ['id', 'player_1', 'player_2', 'status', 'created_at']

class BlockAdmin(admin.ModelAdmin):
    list_display = ['id']

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ['id', 'from_player', 'to_player', 'status', 'match_type']

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['id', 'player_1', 'player_2', 'status', 'type']

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['id', 'match', 'player_1', 'player_2', 'status', 'round_number']


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name','player_1', 'player_2', 'player_3', 'player_4', 'status', 'created_at', 'updated_at']

@admin.register(Winrate)
class WinrateAdmin(admin.ModelAdmin):
    list_display = ['id', 'player', 'victory', 'defeat']
    search_fields = ['player__name']  # Permet de rechercher par nom de joueur
    list_filter = ['player']  # Ajoute un filtre par joueur

admin.site.register(Player, PlayerAdmin)
admin.site.register(Friendship)
admin.site.register(Block)
