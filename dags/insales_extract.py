import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.vault_client import VaultClient
from scripts.insales_client import InSalesClient
from scripts.s3_client import S3Client

def run_extraction ():
    print("------Running Extraction Pipeline-------")

    print("Connectiong to HashiCorp Vault")
    vault = VaultClient()

    print ("------Getting Secrets From Vault ------")
    insales_secrets = vault.get_secret(path="insales_api")
    minio_secrets = vault.get_secret(path="minio_api")

    print("------Client initialization for InSales API------")
    insales_client = InSalesClient (credentials=insales_secrets)

    print("------Getting Products 50 from InSales------")
    products = insales_client.get_products(page=1, per_page=50)

    print(f"-> Успешно скачано товаров: {len(products)}")
    print("------------------\n")

#    for product in products:
#        print(f"ID: {product.id} | Название: {product.title}")
#        print(f"    Категория: {product.category_id}")
#        for variant in product.variants:
#            print(f"  -> Вариант SKU: {variant.sku} | Цена: {variant.price} руб. | Остаток: {variant.quantity} шт.")
#
#        print("-" * 40)

    raw_products_dict = [p.model_dump() for p in products]

    s3_client = S3Client(credentials=minio_secrets)
    s3_client.upload_raw_json(data=raw_products_dict)

if __name__ == "__main__":
    run_extraction()
