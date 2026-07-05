import sys
import os
import io
import json
from datetime import datetime
import requests
from minio import Minio

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

    print("------Client initialization for MinIO (S3)------")
    s3_client = S3Client(credentials=minio_secrets)

    print("------ Extracting Data from InSales to MinIO Bronze ------")

    current_date = datetime.now().strftime("%Y-%m-%d")

    page = 1
    per_page = 100
    total_products = 0

    while True:
        print(f"Fetching page {page}...")
        products = insales_client.get_products(page=page, per_page=per_page)

        if not products:
            print("------ All products have been successfully extracted! ------")
            break

        raw_products_dict = [p.model_dump() for p in products]
        total_products += len(raw_products_dict)

        target_file_path = f"insales/products/{current_date}/page_{page}.json"

        s3_client.upload_raw_json(data=raw_products_dict, file_path=target_file_path)
        
        page += 1

    print(f"-> Успешно скачано товаров: {total_products}")
    print("------------------\n")




if __name__ == "__main__":
    run_extraction()
