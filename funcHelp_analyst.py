import os
from azure.storage.blob import BlobServiceClient

def get_blob_content(blob_url: str) -> bytes:
    """Download blob content using connection string"""
    try:
        conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if conn_str:
            blob_service = BlobServiceClient.from_connection_string(conn_str)
            url_parts = blob_url.replace('%20', ' ').split('/')
            container_name = url_parts[3]
            blob_name = '/'.join(url_parts[4:])
            blob_client = blob_service.get_blob_client(container=container_name, blob=blob_name)
            return blob_client.download_blob().readall()
        return None
    except Exception as e:
        print(f"Blob download error: {e}")
        return None