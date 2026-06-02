import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import boto3
from scripts.vault_client import VaultClient
from scripts.db_client import DBClient

def get_latest_file_from_s3(s3_client, bucket, prefix="insales/products/"):
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    if 'Contents' not in response:
        raise FileNotFouldError("No raw files found in S3")

    sorted_files = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)
    return sorted_files[0]['Key']

def run_silver_transformation():
    print("------Running Silver Tramsformation Pipeline------")

    vault = VaultClient()
    minio_secrets = vault.get_secret(path="minio_api")
    db_secrets = vault.get_secret(path="staging_db")

    s3 = boto3.client(
        's3',
        endpoint_url=minio_secrets.get('endpoint_url', 'http://localhost:9000'),
        aws_access_key_id=minio_secrets['access_key'],
        aws_secret_access_key=minio_secrets['secret_key']
    )
    bucket = minio_secrets.get('bucket_name', 'bronze')

    latest_file_key = get_latest_file_from_s3(s3, bucket)
    print(f"-. Reading data from the file: {latest_file_key}")

    s3_object = s3.get_object(Bucket=bucket, Key=latest_file_key)
    products_data = json.loads(s3_object['Body'].read().decode('utf-8'))

    db = DBClient(credentials=db_secrets)

    print(f"------Processing {len(products_data)} products to Silver Layer------")
    for prod in products_data:
        if not prod.get('sku'):
            prod['sku'] = f"INKNOWN_INSALES-{prod['id']}"

            db.upsert_product_scd2(prod)

    db.close()
    print("Silver Layer UPDATED SUCCESSFULLY")

if __name__ == "__main__":
    run_silver_transformation()
