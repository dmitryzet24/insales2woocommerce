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

def run(one, two):
    """
    Extracts products from InSales shop API as raw JSION files
    """
    print("------Running Extraction Pipeline-------")

    print("Connecting to HashiCorp Vault")
    vault = VaultClient()

    print ("------Getting Secrets From Vault ------")

if __name__: "__main__":
    run_extraction()