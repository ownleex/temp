import uuid
from rest_framework import serializers
from django.db import models
from django.utils import timezone
from shared_models.models import Player, Match, Tournament, Friendship, Block
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from django.contrib.auth.hashers import check_password
from core.validators import validate_strong_password
from django.contrib.auth import authenticate
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django_otp.plugins.otp_totp.models import TOTPDevice
from social_django.utils import load_strategy
import re
import qrcode
import io
import base64
import requests
import tempfile
import os
from django.core.files.base import ContentFile

class PlayerSerializer(serializers.ModelSerializer):
    two_factor_enabled = serializers.BooleanField(read_only=True)

    class Meta:
        model = Player
        fields = [
            'id', 'created_at', 'name', 'avatar', 'online', 'last_seen',
            'description', 'two_factor_enabled'
        ]

    def to_representation(self, instance):
        fields = super().to_representation(instance)
        request = self.context.get('request')
        user = request.user if request and hasattr(request, 'user') else None

        if not user or not user.is_authenticated:
            del fields['online']
            del fields['last_seen']
            del fields['description']
            del fields['two_factor_enabled']
            return fields

        try:
            current_player = user.player_profile
        except AttributeError:
            del fields['online']
            del fields['last_seen']
            del fields['description']
            del fields['two_factor_enabled']
            return fields

        is_self = current_player.id == instance.id
        friendship = Friendship.objects.filter(
            models.Q(player_1=current_player, player_2=instance, status='accepted') |
            models.Q(player_1=instance, player_2=current_player, status='accepted')
        ).first()
        is_friend = is_self or (friendship is not None)

        if not is_friend:
            del fields['online']
            del fields['last_seen']
            del fields['description']

        if not is_self:
            del fields['two_factor_enabled']

        return fields

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = '__all__'


class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'

class FriendshipSerializer(serializers.ModelSerializer):
    player_1_name = serializers.CharField(source='player_1.name')
    player_2_name = serializers.CharField(source='player_2.name')
    status = serializers.CharField()

    class Meta:
        model = Friendship
        fields = ['player_1_name', 'player_2_name', 'status', 'created_at']


class BlockListSerializer(serializers.ModelSerializer):
    blocker = serializers.CharField(source='blocker.name', read_only=True)
    blocked = serializers.CharField(source='blocked.name', read_only=True)

    class Meta:
        model = Block
        fields = ['id', 'blocked', 'blocker','created_at']

#===CRUD PLAYER====

class PlayerRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True, allow_blank=True, allow_null=True)
    password = serializers.CharField(write_only=True, allow_blank=True, allow_null=True)
    password2 = serializers.CharField(write_only=True, allow_blank=True, allow_null=True)


    def validate(self, data):
        username = data.get('username')
        if not username:
            raise serializers.ValidationError({"code": 1009, "message": "Username required."}) # Nom d'utilisateur requis.
        if len(username) > 20:
            raise serializers.ValidationError({"code": 1011, "message": "The username must not exceed 20 characters."}) # Le nom d'utilisateur ne doit pas dépasser 20 caractères.
        if ' ' in username:
            raise serializers.ValidationError({"code": 1012, "message": "The username must not contain spaces."}) # Le nom d'utilisateur ne doit pas contenir d'espaces.
        if not re.match(r'^[a-zA-Z0-9]+$', username):
            raise serializers.ValidationError({"code": 1013, "message": "The username must only contain letters and numbers."}) # Le nom d'utilisateur ne doit contenir que des lettres et des chiffres.
        if Player.objects.filter(name=username).exists():
            raise serializers.ValidationError({"code": 1002, "message": "This username is already taken."})  # Ce nom d'utilisateur est déjà pris.
        
        pwd = data.get('password')
        pwd2 = data.get('password2')
        if not pwd or not pwd2:
            raise serializers.ValidationError({"code": 1010, "message": "Password required."}) # Mot de passe requis.
        if pwd != pwd2:
            raise serializers.ValidationError({"code": 1001, "message": "The passwords do not match."})  # Les mots de passe ne correspondent pas.
        
        validate_strong_password(pwd)
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=f"temp_{uuid.uuid4().hex[:8]}",
            password=validated_data['password']
        )
        player = Player.objects.create(user=user, name=validated_data['username'])
        user.username = f"player_{player.id}"
        user.save()
        return user

    def to_representation(self, instance):
            return {"code": 1000}

class PlayerUpdateInfoSerializer(serializers.ModelSerializer):
    description = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    online = serializers.BooleanField(write_only=True, required=False, allow_null=True)
    avatar = serializers.ImageField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Player
        fields = ['online', 'description', 'avatar']
    
    def validate(self, data):
        # Vérification de l'utilisateur authentifié
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError({"code": 1030, "message": "User not authenticated"})

        # Vérification que l'instance appartient à l'utilisateur
        instance = self.instance
        if instance != request.user.player_profile:
            raise serializers.ValidationError({"code": 1031, "message": "Unauthorized to update this profile"})

        description = data.get('description')
        if description:
            if len(description) > 20:
                raise serializers.ValidationError({"code": 1011, "message": "The description must not exceed 20 characters."}) # La description ne doit pas dépasser 20 caractères.
        
        # Validation de l'image
        avatar = data.get('avatar')
        if avatar:
            # Vérification de l'extension
            allowed_extensions = ['jpg', 'jpeg', 'png']
            if not hasattr(avatar, 'name') or not avatar.name.lower().endswith(tuple(allowed_extensions)):
                raise serializers.ValidationError({"code": 1032, "message": "Invalid file extension"})

            # Vérification de la taille (2 Mo)
            max_weight = 2 * 1024 * 1024
            if avatar.size > max_weight:
                raise serializers.ValidationError({"code": 1033, "message": "Image size exceeds 2MB"})

            try:
                # Vérifier l'intégrité de l'image
                img = Image.open(avatar)
                img.verify()  # Vérifie que c'est une image valide
                avatar.seek(0)  # Réinitialiser le pointeur après verify
                img = Image.open(avatar)  # Ré-ouvrir pour traitement

                # Vérification des dimensions
                max_dimensions = (550, 550)
                if img.width > max_dimensions[0] or img.height > max_dimensions[1]:
                    raise serializers.ValidationError({"code": 1034, "message": "Image dimensions exceed 500x500"})

                # Reconversion pour nettoyer l'image
                output = io.BytesIO()
                img_format = 'PNG' if img.format == 'PNG' else 'JPEG'
                img.save(output, format=img_format, quality=85, optimize=True, exif=b'')  # Supprime les métadonnées
                output.seek(0)

                # Stocker l'image nettoyée dans les données validées
                cleaned_filename = f"avatar.{img_format.lower()}"
                data['avatar'] = ContentFile(output.read(), name=cleaned_filename)

            except Exception as e:
                raise serializers.ValidationError({"code": 1035, "message": f"Invalid image file: {str(e)}"})

        return data

    def update(self, instance, validated_data):
        description = validated_data.get('description')
        online = validated_data.get('online')
        avatar = validated_data.get('avatar')

        # Mise à jour des champs
        if avatar is not None:
            instance.avatar = avatar  # Utiliser l'image nettoyée
        if description is not None:
            instance.description = description
        if online is not None:
            if online:
                instance.online = True
                instance.last_seen = None
            else:
                instance.online = False
                instance.last_seen = timezone.now()

        instance.save()
        return instance

    def to_representation(self, instance):
        return {"code": 1000}

class PlayerUpdateNameSerializer(serializers.ModelSerializer):
    name             = serializers.CharField(write_only=True, allow_blank=True, allow_null=True)
    current_password = serializers.CharField(write_only=True, allow_blank=True, allow_null=True)

    class Meta:
        model = Player
        fields = ['name', 'current_password']


    def validate(self, data):
        user = self.context['request'].user
        if not user.is_authenticated:
            raise serializers.ValidationError({"code": 1030, "message": "Unauthenticated user."})
        
        name = data['name']
        if not re.match(r'^[a-zA-Z0-9]+$', name):
            raise serializers.ValidationError({"code": 1013, "message": "Username must only contain letters and numbers"}) # Le nom d'utilisateur ne doit contenir que des lettres et des chiffres.
        if len(name) > 20:
            raise serializers.ValidationError({"code": 1011, "message": "The username must not exceed 20 characters."}) # Le nom d'utilisateur ne doit pas dépasser 20 caractères.
        if ' ' in name:
            raise serializers.ValidationError({"code": 1012, "message": "The username must not contain spaces."}) # Le nom d'utilisateur ne doit pas contenir d'espaces.
        if Player.objects.filter(name=name).exists():
            raise serializers.ValidationError({"code": 1002, "message": "Username already chosen"}) #Ce nom d'utilisateur est déjà pris.
        
        pwd = data['current_password']
        if not pwd:
            raise serializers.ValidationError({"code": 1010, "message": "Password required."}) # Mot de passe requis.
        if not check_password(pwd, user.password):
            raise serializers.ValidationError({"code": 1008, "message": "Password is incorrect"})  # Mot de passe incorrect.
        return data

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance
    
    def to_representation(self, instance):
        return {"code": 1000}
    
class PlayerUpdatePWDSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_pwd1 = serializers.CharField(write_only=True)
    new_pwd2 = serializers.CharField(write_only=True)

    def validate(self, data):
        user = self.context['request'].user
        cpwd = data.get('current_password')
        pwd  = data.get('new_pwd1')
        pwd2 = data.get('new_pwd2')

        if not pwd or not pwd2 or not cpwd:
            raise serializers.ValidationError({"code": 1010, "message": "Password required."}) # Mot de passe requis.
        if not user.check_password(cpwd):
            raise serializers.ValidationError({"code": 1008, "message": "Password is incorrect"})  # Mot de passe incorrect.
        if pwd != pwd2:
            raise serializers.ValidationError({"code": 1001, "message": "Passwords aren't similar"})  # Les mots de passe ne correspondent pas.
        validate_strong_password(pwd)   # À voir dans validators.py

        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_pwd1'])
        instance.save()
        return instance
    
    def to_representation(self, instance):
        return {"code": 1000}

class PlayerDeleteSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        user = self.context['request'].user
        # Vérifier que l'utilisateur est authentifié
        if not user.is_authenticated:
            raise serializers.ValidationError({"code": 1009, "message": "Unauthenticated user."})
        # Vérifier le mot de passe
        pwd = data.get('password')

        if not pwd:
            raise serializers.ValidationError({"code": 1010, "message": "Password required."}) # Mot de passe requis.
        if not user.check_password(pwd):
            raise serializers.ValidationError({"code": 1008, "message": "Password is incorrect"})  # Mot de passe incorrect.
        return data

    def reset_player(self, player):
        """Réinitialise les champs du joueur."""
        if not player:
            return
        player.forty_two_id = None
        player.name = "[DELETED USER]"
        player.online = False
        player.last_seen = None
        player.avatar = "avatars/default.jpg"
        player.two_factor_enabled = False
        player.save()

    def remove_friend(self, player):
        """Récupère et supprime toutes les relations d'amitié impliquant le joueur."""
        if not player:
            return []
        friendships = Friendship.objects.filter(models.Q(player_1=player) | models.Q(player_2=player))
        friendship_data = [
            {
                "id": friendship.id,
                "player_1": friendship.player_1.id,
                "player_2": friendship.player_2.id
            }
            for friendship in friendships
        ]
        if friendships.exists():
            friendships.delete()
        return friendship_data

    def remove_block(self, player):
        """Récupère et supprime toutes les relations de blocage impliquant le joueur."""
        if not player:
            return []
        blocks = Block.objects.filter(models.Q(blocker=player) | models.Q(blocked=player))
        block_data = [
            {
                "id": block.id,
                "player_1": block.player_1.id,
                "player_2": block.player_2.id
            }
            for block in blocks
        ]
        if blocks.exists():
            blocks.delete()
        return block_data

    def update(self, instance, validated_data):
        """Désactive l'utilisateur et réinitialise les données du joueur."""
        # Récupérer le joueur associé
        player = Player.objects.filter(user=instance).first()

        # Réinitialiser le joueur et supprimer les relations
        self.reset_player(player)
        self.remove_friend(player)
        self.remove_block(player)

        # Désactiver l'utilisateur
        instance.is_active = False
        instance.username = f"deleted_{player.id}"
        instance.save()

        return instance

    def to_representation(self, instance):
        """Retourne une réponse standard pour indiquer le succès."""
        return {
            "code": 1000,
        }

# FONCTION UTILITAIRE pour blacklister tous les tokens d'un utilisateur
def blacklist_all_user_tokens(user):
    """Blacklist tous les refresh tokens actifs d'un utilisateur avec la méthode .blacklist()"""
    try:
        # Récupérer tous les outstanding tokens de l'utilisateur
        outstanding_tokens = OutstandingToken.objects.filter(user=user)
        
        for outstanding_token in outstanding_tokens:
            try:
                # Récréer le RefreshToken à partir du token stocké
                token = RefreshToken(outstanding_token.token)
                # Utiliser la même méthode que dans votre PlayerLogoutSerializer
                token.blacklist()
            except TokenError:
                # Token déjà blacklisté ou invalide, on continue
                pass
            except Exception:
                # Autres erreurs, on continue
                pass
                
    except Exception as e:
        print(f"Erreur lors du blacklisting des tokens: {e}")

class PlayerLoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True, allow_blank=True, allow_null=True)
    password = serializers.CharField(write_only=True, allow_blank=True, allow_null=True)
    otp_code = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
        
    def validate(self, data):
        player_name = data.get('username')
        password = data.get('password')
        otp_code = data.get('otp_code')

        if not player_name:
            raise serializers.ValidationError({"code": 1009, "message": "Username is required"}) # Nom requis
        if not password:
            raise serializers.ValidationError({"code": 1010, "message": "Password is required"}) # Mot de passe requis

        try:
            player = Player.objects.get(name=player_name)
        except Player.DoesNotExist:
            raise serializers.ValidationError({"code": 1013, "message": "Username or Password is incorrect"}) # Nom ou mot de passe incorrect
    
        username = player.user.username
        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError({"code": 1013, "message": "Username or Password is incorrect"}) # Nom ou mot de passe incorrect
        
        # Vérifier 2FA si activé
        if player.two_factor_enabled and player.two_factor_method == 'TOTP':
            if not otp_code:
                raise serializers.ValidationError({"code": 1037, "message": "2FA code is required"})  # Code 2FA requis
            device = TOTPDevice.objects.filter(user=user).first()
            if not device or not device.verify_token(otp_code):
                raise serializers.ValidationError({"code": 1036, "message": "TOTP code is invalid"})  # Code TOTP invalide

        data['user'] = user
        data['player'] = player
        return data

    def create(self, validated_data):
        player = validated_data['player']
        user = validated_data['user']
        
        #Blacklister tous les anciens refresh tokens de cet utilisateur
        blacklist_all_user_tokens(user)
        
        return player

    def to_representation(self, instance):
        # Créer un nouveau refresh token
        refresh = RefreshToken.for_user(instance.user)
        
        return {
            "code": 1000,
            "player": instance.id,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }

class PlayerLogoutSerializer(serializers.Serializer):
    def validate(self, data):
        user = self.context['request'].user
        try:
            player = Player.objects.get(user=user)
        except Player.DoesNotExist:
            raise serializers.ValidationError({"code": 1113, "message": "pas de player associer"})

        data['user'] = user
        data['player'] = player
        return data

    def create(self, validated_data):
        user = validated_data['user']
        player = validated_data['player']
        blacklist_all_user_tokens(user)

        return player

    def to_representation(self, instance):
        return {"code": 1000}

#===CRUD FriendShip====

class SendFriendRequestSerializer(serializers.ModelSerializer):
    player_2 = serializers.IntegerField(write_only=True)

    class Meta:
        model = Friendship
        fields = ['player_2']

    def validate(self, data):
        player_1 = self.context['request'].user
        player_2_id = data.get('player_2')

        try:
            player_2 = Player.objects.get(id=player_2_id)
        except Player.DoesNotExist:
            raise serializers.ValidationError({"code": 1014, "message": "Player doesn't exist"})  # Le joueur cible n'existe pas.
        if player_1 == player_2.user:
            raise serializers.ValidationError({"code": 1015, "message": "You can't add yourself as friend"})  # Vous ne pouvez pas envoyer une demande d'ami à vous-même.
        if Friendship.objects.filter(player_1=player_1.player_profile, player_2=player_2, status='pending').exists():
            raise serializers.ValidationError({"code": 1016, "message": "You already added this player"})  # Une demande d'ami a déjà été envoyée à ce joueur.
        if Friendship.objects.filter(player_1=player_2, player_2=player_1.player_profile, status='pending').exists():
            raise serializers.ValidationError({"code": 1017, "message": "You already received something from this player"})  # Vous avez déjà reçu une demande d'ami de ce joueur.
        if Friendship.objects.filter(
            status='accepted',
            player_1__in=[player_1.player_profile, player_2],
            player_2__in=[player_1.player_profile, player_2]
        ).exists():
            raise serializers.ValidationError({"code": 1002, "message": "You are already friends"})  # Vous êtes déjà amis avec ce joueur.
        if Block.objects.filter(blocker=player_1.player_profile, blocked=player_2).exists():
            raise serializers.ValidationError({"code": 1018, "message": "You blocked this player"})  # Vous avez bloqué ce joueur.
        if Block.objects.filter(blocker=player_2, blocked=player_1.player_profile).exists():
            raise serializers.ValidationError({"code": 1019, "message": "This player blocked you"})  # Ce joueur vous a bloqué.

        return data

    def create(self, validated_data):
        player_1 = self.context['request'].user.player_profile
        player_2_id = validated_data.pop('player_2')
        player_2 = Player.objects.get(id=player_2_id)
        friendship = Friendship.objects.create(player_1=player_1, player_2=player_2, status='pending')
        return friendship

    def to_representation(self, instance):
        return {"code": 1000} 


class FriendRequestAcceptSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)  # Champ pour recevoir l'id dans la requête

    class Meta:
        model = Friendship
        fields = ['id']

    def validate(self, data):
        try:
            friendship = Friendship.objects.get(id=data['id'])
        except Friendship.DoesNotExist:
            raise serializers.ValidationError({"code": 1022, "message": "Friendship request does not exist"})

        request_user = self.context['request'].user

        if friendship.player_2.user != request_user:
            raise serializers.ValidationError({"code": 1020, "message": "Only the recipient can reject this request"})
        if friendship.status != 'pending':
            raise serializers.ValidationError({"code": 1021, "message": "Request has already been processed"})

        # Stocker l'instance dans le contexte pour la méthode update
        self.instance = friendship
        return data

    def update(self, instance, validated_data):
        instance.status = 'accepted'
        instance.save()
        Friendship.objects.get_or_create(
            player_1=instance.player_2,
            player_2=instance.player_1,
            defaults={'status': 'accepted'}
        )
        return instance

    def to_representation(self, instance):
        return {"code": 1000}

class FriendRequestRejectSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Friendship
        fields = ['id']

    def validate(self, data):
        try:
            friendship = Friendship.objects.get(id=data['id'])
        except Friendship.DoesNotExist:
            raise serializers.ValidationError({"code": 1022, "message": "Friendship request does not exist"})  # "Cette demande d'amitié n'existe pas."

        request_user = self.context['request'].user

        if friendship.player_2.user != request_user:
            raise serializers.ValidationError({"code": 1020, "message": "Only the recipient can reject this request"})  # "Seul le destinataire peut rejeter cette demande."
        if friendship.status != 'pending':
            raise serializers.ValidationError({"code": 1021, "message": "Request has already been processed"})  # "Cette demande a déjà été traitée."

        # Stocker l'instance pour la suppression
        self.instance = friendship
        return data

    def to_representation(self, instance):
        return {"code": 1000}
    

class FriendRequestCancelSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Friendship
        fields = ['id']

    def validate(self, data):
        try:
            friendship = Friendship.objects.get(id=data['id'])
        except Friendship.DoesNotExist:
            raise serializers.ValidationError({"code": 1022, "message": "Friendship request does not exist"})  # "Cette demande d'amitié n'existe pas."

        request_user = self.context['request'].user

        if friendship.player_1.user != request_user:
            raise serializers.ValidationError({"code": 1023, "message": "Only the sender can cancel this request"})  # "Seul l'expéditeur peut annuler cette demande."
        if friendship.status != 'pending':
            raise serializers.ValidationError({"code": 1021, "message": "This request has already been processed"})  # "Cette demande a déjà été traitée."

        # Stocker l'instance pour la suppression
        self.instance = friendship
        return data

    def to_representation(self, instance):
        return {"code": 1000}
    

class FriendshipRemoveSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)  # Champ pour recevoir l'id dans la requête

    class Meta:
        model = Friendship
        fields = ['id']

    def validate(self, data):
        try:
            friendship = Friendship.objects.get(id=data['id'])
        except Friendship.DoesNotExist:
            raise serializers.ValidationError({"code": 1022, "message": "Friendship does not exist"})  # "Cette amitié n'existe pas."

        player = self.context['request'].user.player_profile

        if friendship.status != 'accepted':
            raise serializers.ValidationError({"code": 1030, "message": "This relationship is not an accepted friendship"})  # "Cette relation n'est pas une amitié acceptée."
        if friendship.player_1 != player and friendship.player_2 != player:
            raise serializers.ValidationError({"code": 1025, "message": "You are not friends with this player"})  # "Vous n'êtes pas amis avec ce joueur."

        # Stocker l'instance pour la suppression
        self.instance = friendship
        return data

    def to_representation(self, instance):
        return {"code": 1000}

class FriendshipListSerializer(serializers.ModelSerializer):
    player_1 = serializers.CharField(source='player_1.name', read_only=True)
    player_2 = serializers.CharField(source='player_2.name', read_only=True)

    class Meta:
        model = Friendship
        fields = ['id', 'player_1', 'player_2', 'status', 'created_at']


#===CRUD Block====

class BlockPlayerSerializer(serializers.ModelSerializer):
    blocked_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Block
        fields = ['blocked_id']

    def validate(self, data):
        blocker = self.context['request'].user.player_profile
        blocked_id = data.get('blocked_id')

        try:
            blocked = Player.objects.get(id=blocked_id)
        except Player.DoesNotExist:
            raise serializers.ValidationError({"code": 1014, "message": "Player doesn't exist"})  # "Le joueur cible n'existe pas."
        if blocker == blocked:
            raise serializers.ValidationError({"code": 1026, "message": "You can't block yourself"})  # "Vous ne pouvez pas vous bloquer vous-même."
        if Block.objects.filter(blocker=blocker, blocked=blocked).exists():
            raise serializers.ValidationError({"code": 1027, "message": "Player is already blocked"})  # "Ce joueur est déjà bloqué."


        Friendship.objects.filter(
            status='accepted',
            player_1__in=[blocker, blocked],
            player_2__in=[blocker, blocked]
        ).delete()
        Friendship.objects.filter(
            status='pending',
            player_1__in=[blocker, blocked],
            player_2__in=[blocker, blocked]
        ).delete()
        return data

    def create(self, validated_data):
        blocker = self.context['request'].user.player_profile
        blocked_id = validated_data.pop('blocked_id')
        blocked = Player.objects.get(id=blocked_id)
        block = Block.objects.create(blocker=blocker, blocked=blocked)
        return block

    def to_representation(self, instance):
        return {"code": 1000}

class UnblockPlayerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True) 

    class Meta:
        model = Block
        fields = ['id']

    def validate(self, data):
        try:
            block = Block.objects.get(id=data['id'])
        except Block.DoesNotExist:
            raise serializers.ValidationError({"code": 1022, "message": "Block does not exist"})  # "Ce blocage n'existe pas."

        blocker = self.context['request'].user.player_profile

        if block.blocker != blocker:
            raise serializers.ValidationError({"code": 1028, "message": "You have not blocked this player"})  # "Vous n'avez pas bloqué ce joueur."

        # Stocker l'instance pour la suppression
        self.instance = block
        return data

    def to_representation(self, instance):
        return {"code": 1000}


#===2FA====

class Enable2FASerializer(serializers.Serializer):
    otp_code = serializers.CharField(write_only=True, required=False, allow_blank=True)

    def validate(self, data):
        user = self.context['request'].user
        if not user.is_authenticated:
            raise serializers.ValidationError({"code": 1030})  # Utilisateur non authentifié

        otp_code = data.get('otp_code')
        if otp_code and not re.match(r'^\d{6}$', otp_code):
            raise serializers.ValidationError({"code": 1037, "message": "The OTP code must be exactly 6 digits."})
        player = user.player_profile
        device, created = TOTPDevice.objects.get_or_create(user=user, name=f"{player.name}_totp")
        if otp_code and not device.verify_token(otp_code):
            raise serializers.ValidationError({"code": 1036})  # Code TOTP invalide

        return data

    def update(self, instance, validated_data):
        user = self.context['request'].user
        player = instance
        otp_code = validated_data.get('otp_code')

        if otp_code:  # Deuxième étape : valider le code
            player.two_factor_enabled = True
            player.two_factor_method = 'TOTP'
            player.save()
            device, _ = TOTPDevice.objects.get_or_create(user=user, name=f"{player.name}_totp")
            return device

        # Première étape : générer le QR code
        device, _ = TOTPDevice.objects.get_or_create(user=user, name=f"{player.name}_totp")
        return device

    def to_representation(self, instance):
        original_url = instance.config_url
        
        # Récupérer le profil du joueur
        player = self.context['request'].user.player_profile
        
        # Créer le nouveau libellé (seulement le nom du joueur précédé de "Transcendence: ")
        custom_label = f"Transcendence: {player.name}"
        
        # Remplacer uniquement la partie player_X par le nouveau libellé
        modified_url = re.sub(r'totp/([^?]+)', f'totp/{custom_label}', original_url)
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(modified_url)
        qr.make(fit=True)
        
        # Créer une image du QR code
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir l'image en base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        qr_code_image = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        return {
            "code": 1000,
            "method": "TOTP",
            "qr_code_url": modified_url,
            "qr_code_image": f"data:image/png;base64,{qr_code_image}"
        }


class Disable2FASerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = self.context['request'].user
        if not user.is_authenticated:
            raise serializers.ValidationError({"code": 1030, "message": "Unauthenticated user"})  # Utilisateur non authentifié

        password = data.get('password')
        if not password:
            raise serializers.ValidationError({"code": 1010, "message": "Password required."}) # Mot de passe requis.
        if not user.check_password(password):
            raise serializers.ValidationError({"code": 1008, "message": "Password is incorrect"})  # Mot de passe incorrect
        return data

    def update(self, instance, validated_data):
        user = self.context['request'].user
        player = instance
        player.two_factor_enabled = False
        device=TOTPDevice.objects.filter(user=user)
        if device.exists():
            device.delete()
        player.save()
        return player

    def to_representation(self, instance):
        return {"code": 1000}


#===OAUTH====

class Auth42CompleteSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, allow_blank=True, allow_null=True)
    password2 = serializers.CharField(write_only=True, allow_blank=True, allow_null=True)

    def validate(self, data):
        pwd = data.get('password')
        pwd2 = data.get('password2')
        if not pwd or not pwd2:
            raise serializers.ValidationError({"code": 1010, "message": "Password required."})
        if pwd != pwd2:
            raise serializers.ValidationError({"code": 1001, "message": "The passwords do not match."})
        
        validate_strong_password(pwd)
        
        oauth_data = self.context['request'].session.get('oauth_42_data')
        if not oauth_data:
            raise serializers.ValidationError({"code": 1053, "message": "Request failed"})
            
        return data

    def create(self, validated_data):
        request = self.context['request']
        oauth_data = request.session.pop('oauth_42_data', None)
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=f"temp_{uuid.uuid4().hex[:8]}",
            password=validated_data['password']
        )
        
        # Créer le player sans l'avatar
        player = Player.objects.create(
            user=user,
            name=oauth_data['name'],
            forty_two_id=oauth_data['forty_two_id']
        )
        
        # Mettre à jour le nom d'utilisateur final
        user.username = f"42_player_{player.id}"
        user.save()
        
        # Télécharger et enregistrer l'avatar de manière ultra simple
        avatar_url = oauth_data.get('avatar_url')
        if avatar_url:
            try:
                response = requests.get(avatar_url)
                if response.status_code == 200:
                    # Création d'un nom de fichier simple
                    file_name = f"42_avatar_{player.id}.jpg"
                    
                    # Enregistrement direct de l'image
                    from django.core.files.base import ContentFile
                    player.avatar.save(
                        file_name,
                        ContentFile(response.content),
                        save=True
                    )
            except Exception as e:
                # En cas d'erreur, on utilise l'avatar par défaut
                print(f"Erreur lors du téléchargement de l'avatar: {str(e)}")
        
        return player

    def to_representation(self, instance):
        return {
            "code": 1000,
            "name": instance.name,
        }
