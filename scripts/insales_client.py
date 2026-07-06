import requests
from typing import List
from scripts.models import InSalesProduct

class InSalesClient:
    def __init__(self, credentials: dict):
        self.shop_url = credentials['shop_url'].strip('/')
        self.api_key = credentials['api_key']
        self.password = credentials['password']

        self.base_url = f"https://{self.api_key}:{self.password}@{self.shop_url}/admin"

    def get_products(self, page: int = 1, per_page: int = 100) -> List[InSalesProduct]:
        url = f"{self.base_url}/products.json"
        params = {
            "page": page,
            "per_page": per_page
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            raw_products = response.json()
            validated_prosucts = []

            for item in raw_products:
                product = InSalesProduct(**item)
                validated_prosucts.append(product)

            return validated_prosucts

        except requests.exceptions.RequestException as e:
            raise RuntimeError (f"API request error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Validation error: {str(e)}")

    def get_orders(self, page: int = 1, per_page: int = 100) -> List[InSalesProduct]:
        url = f"{self.base_url}/orders.json"
        params = {
            "page": page,
            "per_page": per_page
        }

        try:
            response = request.get(url, params=params, timeout=10)
            response.raise_for_status()

            raw_products = response.json()

            # validated_prosucts = []
            # for item in raw_products:
            #     product = InSalesProduct(**item)
            #     validated_prosucts.append(product)

            return raw_products
        except requests.exceptions.RequestException as e:
            raise RuntimeError (f"API request error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Validation error: {str(e)}")