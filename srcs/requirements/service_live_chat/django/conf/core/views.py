from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from .models import PrivateMessage, GeneralMessage
from .serializers import PrivateMessageSerializer, GeneralMessageSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from shared_models.models import Player, Block
from django.db.models import Q
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse

@method_decorator(csrf_exempt, name='dispatch')
class StatusApi(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({"code": 1000})
    
@method_decorator(csrf_exempt, name='dispatch')
class GeneralMessageListView(generics.ListAPIView):
    serializer_class = GeneralMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            player = Player.objects.get(user=user)
        except Player.DoesNotExist:
            raise ValidationError({"code": 2008, "message": "Player profile not found"})  # Profil de joueur non trouvé

        blocked_by_user = Block.objects.filter(blocker=player).values_list('blocked', flat=True)
        blocked_by_others = Block.objects.filter(blocked=player).values_list('blocker', flat=True)
        excluded_players = set(blocked_by_user).union(set(blocked_by_others))

        queryset = GeneralMessage.objects.exclude(sender__in=excluded_players).order_by('-timestamp')
        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({"code": 1000, "data": response.data})

@method_decorator(csrf_exempt, name='dispatch')
class GeneralMessageSendView(generics.CreateAPIView):
    queryset = GeneralMessage.objects.all()
    serializer_class = GeneralMessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        message = serializer.save()
        message_data = GeneralMessageSerializer(message).data
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "general_chat",
            {
                "type": "chat_message",
                "message": message_data
            }
        )

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return response

@method_decorator(csrf_exempt, name='dispatch')
class PrivateMessageListView(generics.ListAPIView):
    serializer_class = PrivateMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            player = Player.objects.get(user=user)
        except Player.DoesNotExist:
            raise ValidationError({"code": 2009, "message": "Player profile not found"})  # Profil de joueur non trouvé

        blocked_by_user = Block.objects.filter(blocker=player).values_list('blocked', flat=True)
        blocked_by_others = Block.objects.filter(blocked=player).values_list('blocker', flat=True)
        excluded_players = set(blocked_by_user).union(set(blocked_by_others))

        queryset = PrivateMessage.objects.filter(
            Q(sender=player) | Q(receiver=player)
        ).exclude(
            Q(sender__in=excluded_players) | Q(receiver__in=excluded_players)
        )

        receiver_id = self.request.query_params.get('receiver_id')
        if receiver_id:
            try:
                receiver = Player.objects.get(id=receiver_id)
                if receiver.id in excluded_players:
                    raise ValidationError({"code": 2011, "message": "You cannot see messages from a blocked player"})  # Vous ne pouvez pas voir les messages d'un joueur bloqué
                queryset = queryset.filter(
                    Q(sender=player, receiver=receiver) | Q(sender=receiver, receiver=player)
                )
            except Player.DoesNotExist:
                raise ValidationError({"code": 2010, "message": "Recipient player not found"})  # Joueur destinataire non trouvé

        return queryset.order_by('-timestamp')

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({"code": 1000, "data": response.data})

@method_decorator(csrf_exempt, name='dispatch')
class PrivateMessageSendView(generics.CreateAPIView):
    queryset = PrivateMessage.objects.all()
    serializer_class = PrivateMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['receiver_player_id'] = self.kwargs['receiver_player_id']
        return context

    def perform_create(self, serializer):
        message = serializer.save()
        sender_player = message.sender
        receiver_player = message.receiver
        message_data = PrivateMessageSerializer(message).data
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"private_chat_{sender_player.id}",
            {
                "type": "chat_message",
                "message": message_data
            }
        )
        async_to_sync(channel_layer.group_send)(
            f"private_chat_{receiver_player.id}",
            {
                "type": "chat_message",
                "message": message_data
            }
        )

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return response

def health_check(request):
    return JsonResponse({"status": "ok"})
