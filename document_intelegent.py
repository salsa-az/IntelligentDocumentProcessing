import json
import os
from datetime import datetime, timedelta,timezone 
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
from funcHelp_analyst import get_blob_content
from dotenv import load_dotenv
load_dotenv()
# Azure Document Intelligence setup
AZURE_DOC_INTELLIGENCE_ENDPOINT = os.getenv("AZURE_DOC_INTELLIGENCE_ENDPOINT")
AZURE_DOC_INTELLIGENCE_KEY = os.getenv("AZURE_DOC_INTELLIGENCE_KEY")
CUSTOM_MODEL_ID = os.getenv("CUSTOM_MODEL_ID")

document_intelligence_client = DocumentIntelligenceClient(
    endpoint=AZURE_DOC_INTELLIGENCE_ENDPOINT,
    credential=AzureKeyCredential(AZURE_DOC_INTELLIGENCE_KEY)
)
def get_sas_url(blob_add):

    try:
        # 1. Ambil connection string dari environment variable
        connect_str = os.environ["BLOB_STRING_CONECTION"]
        
        # 2. Buat client menggunakan connection string
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)

        # Ambil nama akun dan kunci dari client untuk membuat SAS
        account_name = blob_service_client.account_name
        account_key = blob_service_client.credential.account_key
        container_name = os.environ["AZURE_STORAGE_CONTAINER_NAME"] # Ini masih kita butuhkan


        print(f"Permintaan valid untuk blob: {blob_add}. Membuat SAS URL...")

        # 3. Buat SAS token menggunakan account key
        #    Kita tidak lagi menggunakan user_delegation_key
        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=container_name,
            blob_name=blob_add,
            account_key=account_key, # Gunakan account key
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(minutes=1)
        )

        sas_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_add}?{sas_token}"
        
        return sas_url
    except Exception as e:
        return f"error : Environment variable tidak ditemukan: {e}"

def analize_doc(blob_add) :
    sas_url_dokumen = get_sas_url("Input_document/invoice/Doc005.pdf")
    print("✅ SAS URL sementara berhasil didapatkan.")

    # 2. Gunakan SAS URL untuk memanggil Document Intelligence
    print("Memanggil Document Intelligence...")
    poller = document_intelligence_client.begin_analyze_document(
        model_id="prebuilt-invoice",
        body=AnalyzeDocumentRequest(url_source=sas_url_dokumen)
    )
    result = poller.result()
    print("✅ Dokumen berhasil dianalisis.")