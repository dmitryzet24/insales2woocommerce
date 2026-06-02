import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.vault_client import VaultClient
from scripts.insales_client import InSalesClient

def run_extraction ():
    print("------Running Extraction Pipeline-------")

    print("Connectiong to HashiCorp Vault")
    vault = VaultClient()

    print ("------Getting Secrets From Vault ------")
    insales_secrets = vault.get_secret(path="insales_api")

    print("------Client initialization for InSales API------")
    insales_client = InSalesClient (credentials=insales_secrets)

    print("------Getting Products from InSales------")
    products = insales_client.get_products(page=1, per_page=50)

    print(f"-> Успешно скачано товаров: {len(products)}")
    print("------------------\n")

    for product in products:
        print(f"ID: {product.id} | Название: {product.title}")
        print(f"    Категория: {product.category_id}")
        for variant in product.variants:
            print(f"  -> Вариант SKU: {variant.sku} | Цена: {variant.price} руб. | Остаток: {variant.quantity} шт.")

        print("-" * 40)

if __name__ == "__main__":
    run_extraction()
