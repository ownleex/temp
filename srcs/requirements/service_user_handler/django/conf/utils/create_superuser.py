import os
import sys
import django
import hvac
from django.core.management import call_command
from django.contrib.auth import get_user_model

# Token extract
with open('/django_web_app/user_handler_django/user_handler_django', 'r') as file:
    vault_token = file.read().strip()

# Vault client create
client = hvac.Client(url='http://vault:8200', token=vault_token)

if not client.is_authenticated():
    raise Exception("Authentification échouée avec Vault")

keys = [
    'django_super_user_name',
    'django_super_user_password',
    'django_super_user_email'
]

secrets = {}

# Vault secrets recover
for key in keys:
    response = client.secrets.kv.v1.read_secret(path=f'user_handler/django/{key}')
    secrets[key] = response['data'].get(key)

# Django prepare context
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_user_handler.settings')
django.setup()

# Secrets recover
username = secrets['django_super_user_name']
email = secrets['django_super_user_email']
password = secrets['django_super_user_password']

if not all([username, email, password]):
    print("Please define SUPER_USER_NAME, SUPER_USER_EMAIL and SUPER_USER_PASSWORD secrets.")
    sys.exit(1)

# Vérifier si le superutilisateur existe
User = get_user_model()
if User.objects.filter(username=username).exists():
    print(f"Super '{username}' already exist.")
    sys.exit(0)

# Superuser create
call_command('createsuperuser', username=username, email=email, interactive=False)

# Password define
user = User.objects.get(username=username)
user.set_password(password)
user.save()
