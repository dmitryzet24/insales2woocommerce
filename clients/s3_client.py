import io
import json
import boto3
from datetime import datetime

class S3Client:
    def __init__(self, credentials: dict):
        print("------Client initialization for MinIO (S3)------")

        self.s3 = boto3.client(
                's3',
                endpoint_url=credentials.get('endpoint_url', 'http://host.docker.internal:9000'),
                aws_access_key_id=credentials['access_key'],
                aws_secret_access_key=credentials['secret_key']
        )
        self.bucket_name = credentials.get('bucket_name', 'bronze')

        try:
            self.s3.head_bucket(Bucket=self.bucket_name)
        except:
            print(f"------Bucket '{self.bucket_name}' hasn't been found. Creating a new one...")
            self.s3.create_bucket(Bucket=self.bucket_name)
        
    def file_exists(self, file_path: str) -> bool:
        try:
            self.s3.head_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except:
            return False

    def upload_raw_json(self, data: list, file_path: str):
        print(f"------Uploading raw data to MinIO bucket: {self.bucket_name}------")

        current_date = datetime.now().strftime("%Y-%m-%d")

        json_buffer = io.BytesIO(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))

        try:
            self.s3.upload_fileobj(json_buffer, self.bucket_name, file_path)
            print(f"-> File successfully uploaded to S3: {file_path}")
            return file_path
        except Exception as e:
            raise RuntimeError(f"Error during upload to MinIO has emerged: {str(e)}")

    # def upload_orders_partitioned(self, orders_data: list):
    #     """
    #     Automatically partitions orders by year/month/day
    #     """

