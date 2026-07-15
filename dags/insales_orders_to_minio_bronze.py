import os
import sys
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clients.vault_client import VaultClient
from clients.insales_client import InSalesClient
from clients.s3_client import S3Client


def run_orders_extraction(**context):
    print("------ Running Orders Extraction Pipeline -------")

    print("Connecting to HashiCorp Vault...")
    vault = VaultClient()

    print("------ Getting Secrets From Vault ------")
    insales_secrets = vault.get_secret(path="insales_api")
    minio_secrets = vault.get_secret(path="minio_api")

    print("------ Client initialization for InSales API ------")
    insales_client = InSalesClient(credentials=insales_secrets)

    print("------ Client initialization for MinIO (S3) ------")
    s3_client = S3Client(credentials=minio_secrets)

    current_date = context["ds"]
    print(f"Target date for orders extraction (by updated_at): {current_date}")

    print("------ Extracting Changed Orders from InSales to MinIO Bronze ------")

    page = 1
    per_page = 100
    total_orders = 0

    while True:
        target_file_path = f"insales/orders/{current_date}/page_{page}.json"

        # Idempotency check
        if s3_client.file_exists(target_file_path):
            print(f"Page {page} for orders already exists in MinIO. Skipping HTTP request...")
            page += 1
            continue

        print(f"Fetching page {page} for updated date {current_date}...")
        
        orders = insales_client.get_orders(date=current_date, page=page, per_page=per_page)

        if not orders:
            print("------ All changed orders for this day have been successfully extracted! ------")
            break

        raw_orders_dict = [
            o.model_dump() if hasattr(o, "model_dump") else o for o in orders
        ]
        total_orders += len(raw_orders_dict)

        s3_client.upload_raw_json(data=raw_orders_dict, file_path=target_file_path)
        
        page += 1

    print(f"-> Total orders fetched/updated on {current_date}: {total_orders}")
    print("------------------\n")


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False
}

with DAG(
    dag_id="insales_orders_to_minio_bronze",
    default_args=default_args,
    description="Extract updated and new orders from InSales API and upload to MinIO Bronze",
    schedule="@daily",
    start_date=datetime(2014, 1, 1),
    catchup=False,
    tags=["insales", "bronze", "orders"],
) as dag:

    extract_orders_task = PythonOperator(
        task_id="extract_insales_orders",
        python_callable=run_orders_extraction,
    )

    extract_orders_task