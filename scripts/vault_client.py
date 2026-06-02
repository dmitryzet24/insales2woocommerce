import os
import hvac

class VaultClient:
    def __init__(self):
        self.vault_url = os.getenv("VAULT_ADDR", "http://localhost:8200")       # For local tests
        self.vault_token = os.getenv("VAULT_TOKEN", "root_token_local")         # For local tests
    
        self.client = hvac.Client(url=self.vault_url, token=self.vault_token) 
        if not self.client.is_authenticated():
            raise ConnectionError("Authorisation failed in HashiCorp Vault!")

    def get_secret(self, path: str) -> dict:
        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                mount_point='secret', 
                path=path
            )
            return response['data']['data']
        except Exception as e:
            raise RuntimeError(self._format_error(path, e))

    def _format_error(self, path: str, error: Exception) -> str:
        return f"Error in Vault response '{path}' из Vault: {str(error)}"