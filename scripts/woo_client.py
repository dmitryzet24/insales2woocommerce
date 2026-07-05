from woocommerce import API
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # For local tests

class WooCommerceClient:
    def __init__(self, credentials: dict):
        print("------Client initialization for WooCommerce (Gold)------")

        self.wcapi = API(
            url="https://wpobrf.pulapula.dev",
            consumer_key=credentials.get('consumer_key'),
            consumer_secret=credentials.get('consumer_secret'),
            version="wc/v3",
            query_string_auth=True,
            wp_api=True,
            is_ssl=False # For local tests
        )
    
    def get_product_by_sku(self, sku: str):
        response = self.wcapi.get("products", params={"sku": sku}).json()
        if response and isinstance(response, list) and len(response) > 0:
            return response[0]
        return None
    
    def create_product(self, product_data: dict):
        data = {
            "name": product_data['title'],
            "type": "simple",
            "regular_price": str(product_data['price']),
            "sku": product_data['sku'],
            "manage_stock": False
        }
        response = self.wcapi.post("products", data)
        if response.status_code in [200, 201]:
            print(f"[CREATE] Product SKU {product_data['sku']} successfully created in Woo.")
        else:
            print(f"[ERROR] Appeared when creating SKU {product_data['sku']}: {response.text}")


    def update_product(self, woo_id: int, product_data: dict):
        data = {
            "name": product_data['title'],
            "regular_price": str(product_data['price'])
        }
        response = self.wcapi.put(f"products/{woo_id}", data)
        if response.status_code == 200:
            print(f"[UPDATE] Product SKU {product_data['sku']} successfully added to Woo.")
        else:
            print(f"[ERROR] Appeared when adding SKU {product_data['sku']}: {response.text}")
