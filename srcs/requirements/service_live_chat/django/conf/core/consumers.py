import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class GeneralChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.player_id = self.scope.get('player_id')

        await self.accept()

        if not self.user.is_authenticated:
            await self.send(text_data=json.dumps({
                "code": 3012, "message": "Unauthenticated user"  # Utilisateur non authentifié
            }))
            await self.close(code=3012)
            return

        self.group_name = "general_chat"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.send(text_data=json.dumps({
            "code": 1000  # Connexion réussie
        }))

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    @database_sync_to_async
    def is_blocked(self, sender_player_id):
        from shared_models.models import Player, Block
        """Vérifie si le joueur connecté a bloqué ou est bloqué par le sender."""
        try:
            current_player = Player.objects.get(id=self.player_id)
            sender_player = Player.objects.get(id=sender_player_id)
            return (Block.objects.filter(blocker=current_player, blocked=sender_player).exists() or
                    Block.objects.filter(blocker=sender_player, blocked=current_player).exists())
        except Player.DoesNotExist:
            return True  # Si un joueur n'existe pas, on bloque par sécurité

    async def chat_message(self, event):
        message = event['message']
        sender_id = message.get('sender')

        # Vérifier si le joueur connecté a bloqué ou est bloqué par le sender
        is_blocked = await self.is_blocked(sender_id)
        if not is_blocked:
            await self.send(text_data=json.dumps({
                'message': message
            }))

class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        player_id = self.scope.get('player_id')

        await self.accept()

        if not user.is_authenticated or player_id is None:
            await self.send(text_data=json.dumps({
                "code": 3014, "message": "Unauthenticated user or no associated player"  # Utilisateur non authentifié ou aucun joueur associé
            }))
            await self.close(code=3014)
            return

        self.player_id = self.scope['url_route']['kwargs']['player_id']
        if str(player_id) != self.player_id:
            await self.send(text_data=json.dumps({
                "code": 3015, "message": "Inconsistency between player ID in token and URL" # Incohérence entre l'ID du joueur dans le token et l'URL
            }))
            await self.close(code=3015)
            return

        self.group_name = f"private_chat_{self.player_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.send(text_data=json.dumps({
            "code": 1000  # Connexion réussie
        }))

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        pass 

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
