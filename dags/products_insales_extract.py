from airflow import DAG
from airflow.operators.python import PythonOperator

import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clients.vault_client import VaultClient
from clients.insales_client import InSalesClient
from clients.s3_client import S3Client


def run_extraction(**context):

    print("------ Running Extraction Pipeline -------")

    print("Connecting to HashiCorp Vault")
    vault = VaultClient()

    print("------ Getting Secrets From Vault ------")
    insales_secrets = vault.get_secret(path="insales_api")
    minio_secrets = vault.get_secret(path="minio_api")

    print("------ Client initialization for InSales API ------")
    insales_client = InSalesClient(credentials=insales_secrets)

    print("------ Client initialization for MinIO (S3) ------")
    s3_client = S3Client(credentials=minio_secrets)

    print("------ Extracting Data from InSales to MinIO Bronze ------")

    current_date = context["ds"]
    print(f"Target date for extraction: {current_date}")

    page = 1
    per_page = 100
    total_products = 0

    while True:
        target_file_path = f"insales/products/{current_date}/page_{page}.json"

        if s3_client.file_exists(target_file_path):
            print(f"Page {page} already exists in MinIO. Skipping HTTP request...")
            # page += 1
            continue

        print(f"Fetching page {page}...")
        products = insales_client.get_products(page=page, per_page=per_page)

        if not products:
            print("------ All products have been successfully extracted! ------")
            break

        raw_products_dict = [p.model_dump() for p in products]
        total_products += len(raw_products_dict)

        s3_client.upload_raw_json(data=raw_products_dict, file_path=target_file_path)
        
        page += 1

    print(f"-> Products successfully fetched: {total_products}")
    print("------------------\n")


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="insales_to_minio_bronze",
    default_args=default_args,
    description="Extract products from InSales API and upload to MinIO Bronze layer",
    schedule="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["insales", "bronze", "extraction"],
) as dag:

    extract_task = PythonOperator(
        task_id="extract_insales_products",
        python_callable=run_extraction,
    )

    extract_task
