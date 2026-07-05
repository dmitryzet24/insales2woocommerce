import os
import hvac
from dotenv import load_dotenv

load_dotenv()

class VaultClient:
    def __init__(self):
        self.vault_url = os.getenv("VAULT_ADDR")
        self.vault_token = os.getenv("VAULT_TOKEN")
    
        self.client = hvac.Client(url=self.vault_url, token=self.vault_token) 

        try:
            if not self.client.is_authenticated():
                raise ConnectionError("Authorization failed in HashiCorp Vault! Check your token configuration.")
        except Exception as e:
            raise ConnectionError(f"Cannot connect to Vault server: {str(e)}")

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
        return f"Error in Vault response '{path}' from Vault: {str(error)}"