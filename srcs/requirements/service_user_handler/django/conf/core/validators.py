import re
from rest_framework import serializers


def validate_strong_password(password):
    if len(password) < 8:
        raise serializers.ValidationError({"code": 1003, "message": "Password is not strong enough.\nPassword must contain at least 8 characters."})  # Le mot de passe doit contenir au moins 8 caractères.
    if len(password) > 50:
        raise serializers.ValidationError({"code": 1103, "message": "Password is not strong enough.\nPassword must contain max 50 characters."})  # Le mot de passe doit contenir au moins 8 caractères.
    if not any(char.isdigit() for char in password):
        raise serializers.ValidationError({"code": 1004, "message": "Password is not strong enough.\nPassword must contain at least one number."})  # Le mot de passe doit contenir au moins un chiffre.
    if not any(char.islower() for char in password):
        raise serializers.ValidationError({"code": 1005, "message": "Password is not strong enough.\nPassword must contain at least one lowercase letter"})  # Le mot de passe doit contenir au moins une lettre minuscule.
    if not any(char.isupper() for char in password):
        raise serializers.ValidationError({"code": 1006, "message": "Password is not strong enough.\nPassword must contain at least one capital letter."})  # Le mot de passe doit contenir au moins une lettre majuscule.
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise serializers.ValidationError({"code": 1007, "message": "Password is not strong enough.\nPassword must contain at least one special character (!@#$%^&*...)."})  # Le mot de passe doit contenir au moins un caractère spécial.
