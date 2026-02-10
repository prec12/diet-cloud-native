"""
upload_to_azurite.py
Uploads All_Diets.csv to Azurite Blob Storage (local emulator).
Creates container 'datasets' if it doesn't exist.
"""

import os
from azure.storage.blob import BlobServiceClient

AZURITE_CONNECTION_STRING = (
    "DefaultEndpointsProtocol=http;"
    "AccountName=devstoreaccount1;"
    "AccountKey="
    "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/"
    "K1SZFPTOtr/KBHBeksoGMGw==;"
    "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
)

CONTAINER_NAME = "datasets"
LOCAL_FILE = os.path.join("data", "All_Diets.csv")
BLOB_NAME = "All_Diets.csv"

def main():
    if not os.path.exists(LOCAL_FILE):
        raise FileNotFoundError(f"Missing file: {LOCAL_FILE}")

    service = BlobServiceClient.from_connection_string(AZURITE_CONNECTION_STRING)
    container = service.get_container_client(CONTAINER_NAME)

    # Create container if missing
    try:
        container.create_container()
        print(f"Created container: {CONTAINER_NAME}")
    except Exception:
        print(f"Container already exists: {CONTAINER_NAME}")

    blob = container.get_blob_client(BLOB_NAME)

    with open(LOCAL_FILE, "rb") as f:
        blob.upload_blob(f, overwrite=True)

    print(f"Uploaded {LOCAL_FILE} to container '{CONTAINER_NAME}' as blob '{BLOB_NAME}'")

if __name__ == "__main__":
    main()
