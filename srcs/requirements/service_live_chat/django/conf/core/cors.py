from django.conf import settings

def get_cors_origins():
    """Retourne la liste des origines autorisées pour CORS."""
    return settings.CORS_ALLOWED_ORIGINS

# Créer une classe middleware pour valider les origines CORS
class CorsOriginValidator:
    def __init__(self, app):
        self.app = app
        self.allowed_origins = get_cors_origins()

    async def __call__(self, scope, receive, send):
        # Vérifier l'origine de la connexion WebSocket
        origin = None
        for header_name, header_value in scope['headers']:
            if header_name == b'origin':
                origin = header_value.decode('utf-8')
                break

        # Si l'origine est dans la liste des origines autorisées, continuer
        if origin in self.allowed_origins:
            return await self.app(scope, receive, send)
        
        # Sinon, fermer la connexion
        await send({
            'type': 'websocket.close',
            'code': 403,
        })
