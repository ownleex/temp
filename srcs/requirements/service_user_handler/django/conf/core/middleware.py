from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.authentication import JWTAuthentication
from shared_models.models import Player
from django.http import JsonResponse
import json
import re

class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()
        self.last_cleanup = timezone.now()
        self.cleanup_interval = timedelta(minutes=5) #Nettoyage toutes les x minutes

    def __call__(self, request):
        #Mise à jour des utilisateurs connectés
        try:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Bearer '):
                validated_token = self.jwt_auth.get_validated_token(auth_header.split(' ')[1])
                user = self.jwt_auth.get_user(validated_token)
                
                #Mettre à jour le statut en ligne
                try:
                    player = user.player_profile
                    player.online = True
                    player.last_seen = timezone.now()
                    player.save(update_fields=['online', 'last_seen'])
                except Player.DoesNotExist:
                    pass
        except Exception:
            pass

        #Vérifier les utilisateurs inactifs (périodiquement)
        now = timezone.now()
        if now - self.last_cleanup > self.cleanup_interval:
            self.cleanup_inactive_users()
            self.last_cleanup = now

        return self.get_response(request)

    def cleanup_inactive_users(self):
        """Marque les utilisateurs inactifs comme hors ligne."""
        try:
            inactive_time = timezone.now() - timedelta(minutes=10) # Considérer comme inactif après x minutes sans activité
            Player.objects.filter(online=True, last_seen__lt=inactive_time).update(online=False)
        except Exception as e:
            print(f"Erreur lors du nettoyage des utilisateurs inactifs: {e}")

class SetUserOnlineMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()

    def __call__(self, request):
        # Mettre l'utilisateur en ligne si un token valide est utilisé
        try:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Bearer '):
                validated_token = self.jwt_auth.get_validated_token(auth_header.split(' ')[1])
                user = self.jwt_auth.get_user(validated_token)
                
                # Mettre à jour le statut en ligne
                try:
                    player = user.player_profile
                    player.online = True
                    player.last_seen = timezone.now()
                    player.save(update_fields=['online', 'last_seen'])
                except AttributeError:  # Si player_profile n'existe pas
                    pass
        except Exception:
            pass

        return self.get_response(request)

class XSSProtectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in ('POST', 'PATCH'):
            # Regex combinée pour XSS et SQL
            malicious_pattern = re.compile(
                r'[<>\'";]|--|/\*|\*/|script|on(click|load|mouseover|mouseout|submit|change|focus|blur|keypress|keydown|keyup)|(\b(union|select|insert|delete|update|drop|alter|exec|create|truncate|grant|revoke)\b\s*(all|from|into|set|table)?\s*[^\w])',
                re.IGNORECASE
            )
            if request.content_type == 'application/json':
                try:
                    data = json.loads(request.body)
                    for key, value in data.items():
                        if isinstance(value, str) and malicious_pattern.search(value):
                            return JsonResponse({"code": 1100, "message": f"Characters not allowed in {key}"}, status=400)
                except json.JSONDecodeError:
                    return JsonResponse({"code": 1015, "message": "JSON invalid"}, status=400)
            elif request.content_type.startswith('multipart/form-data'):
                for key, value in request.POST.items():
                    if malicious_pattern.search(value):
                        return JsonResponse({"code": 1100, "message": f"Characters not allowed in {key}"}, status=400)
        return self.get_response(request)
