import json
import os, re
from datetime import datetime, timedelta,timezone 
from azure.core.credentials import AzureKeyCredential
from typing import Dict, Any
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
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
document_analysis_client = DocumentAnalysisClient(
        endpoint=AZURE_DOC_INTELLIGENCE_ENDPOINT, credential=AzureKeyCredential(AZURE_DOC_INTELLIGENCE_KEY)
)
def normalize_key(k: str, keep_colon: bool=False) -> str:
    s = k.replace('\n', ' ').strip()
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'\s*:\s*$', '', s)
    return s + ' :' if keep_colon else s

def clean_simple_value(key: str, v):
    if not isinstance(v, str):
        return v
    s = v.replace('\n', ' ').strip()
    s = re.sub(r'\s+', ' ', s)
    if 'nip' in key.lower():
        digits = re.sub(r'\D', '', s)
        return digits
    s = re.sub(r'\s*([.,:;()\-\/])\s*', r'\1 ', s).strip()
    s = re.sub(r'\s+([%.\,])', r'\1', s)
    return s

def clean_document(data: dict):
    top_fields = {}
    for k, v in data.items():
        if k == 'All content':
            continue
        nk = normalize_key(k, keep_colon=False)
        top_fields[nk] = clean_simple_value(nk, v) if isinstance(v, str) else v
    top_vals = list(top_fields.values())
    return top_fields
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


def get_result(sas_url_dokumen, document_type) :
    """Analyze the document using the specified model."""
    print(f"Memproses dokumen dengan model: {document_type}")
    try :
        poller = document_analysis_client.begin_analyze_document_from_url("prebuilt-document", sas_url_dokumen)
        result = poller.result()  
    except Exception as e :
        print(f"Error during document analysis: {e}")
        return {"error" : str(e)}
    return result
# parser function
def card_parser(result) :
    """Parse the document analysis result."""
    all_result = {}
    for kv_pair in result.key_value_pairs:
        if kv_pair.key and kv_pair.value:
            all_result[kv_pair.key.content] = kv_pair.value.content
        else:
            all_result[kv_pair.key.content] = "-"
    all_result = clean_document(all_result)
    return all_result

def map_insurance_and_id_card(card, document_type):
    """Map fields from insurance card and ID card according to the specified criteria."""
    if document_type=="insuranceCard":
        # Extract relevant fields from insurance card
        mapped_insurance = {
            "No. Kartu": card.get("No. Kartu", ""),
            "No. Polis": card.get("No. Polis", ""),
            "No. Peserta": card.get("No. Peserta", "")
        }
        return mapped_insurance
    elif document_type=="idCard":
        # Extract all fields from ID card except "Berlaku Hingga"
        mapped_id_card = {key: value for key, value in card.items() if key != "Berlaku Hingga"}
        return mapped_id_card
    return {}

def analize_doc(blob_add : str, document_type :str) :
    try : 
        sas_url_dokumen = get_sas_url(blob_add)
        print(f"SAS URL generated")
        result = get_result(sas_url_dokumen, document_type)
        print(f"Document analyzed successfully.")
        parsed = card_parser(result)
        print(f"Document parsed successfully.")
        mapout = map_insurance_and_id_card(parsed, document_type)
        print(f"Document mapped successfully.")
        return mapout
    except Exception as e :
        print(f"Error during document analysis: {e}")
        return {"error" : str(e)}
