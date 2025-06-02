import hvac

def get_vault_secrets():
    vault_token_path = './live_chat_django/live_chat_django'
    vault_url = 'http://vault:8200'

    keys = [
        'domain_name',
        'django_secret_key',
        'postgres_password',
        'postgres_host',
        'postgres_port',
        'postgres_user',
        'postgres_database_name',
        'django_super_user_name',
        'django_super_user_password',
        'django_super_user_email'
    ]

    while True:
        try:
            # Token read
            with open(vault_token_path, 'r') as file:
                vault_token = file.read().strip()

            # Vault client create
            client = hvac.Client(url=vault_url, token=vault_token)

            secrets = {}

            # Recover each token
            for key in keys:
                response = client.secrets.kv.v1.read_secret(path=f'live_chat/django/{key}')
                secrets[key] = response['data'].get(key)
                if secrets[key] is None:
                    raise Exception(f"'{key}' key is empty")

            return secrets

        except Exception as e:
            print(f"{e}")
