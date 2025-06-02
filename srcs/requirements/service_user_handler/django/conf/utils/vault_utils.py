import hvac

def get_vault_secrets():
    vault_token_path = './user_handler_django/user_handler_django'
    vault_url = 'http://vault:8200'

    keys = [
        'domain_name',
        'django_secret_key',
        'postgres_password',
        'postgres_host',
        'postgres_port',
        'postgres_user',
        'postgres_database_name',
        'auth_42_key',
        'auth_42_secret'
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
                response = client.secrets.kv.v1.read_secret(path=f'user_handler/django/{key}')
                secrets[key] = response['data'].get(key)
                if secrets[key] is None:
                    raise Exception(f"'{key}' key is empty")

            return secrets

        except Exception as e:
            print(f"{e}")
