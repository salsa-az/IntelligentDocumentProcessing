import json
import os
from datetime import datetime, timedelta,timezone 
from azure.core.credentials import AzureKeyCredential
from typing import Dict, Any
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
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


def get_result(sas_url_dokumen, model_name) :
    poller = document_intelligence_client.begin_analyze_document(
        model_id=model_name,
        body=AnalyzeDocumentRequest(url_source=sas_url_dokumen)
    )
    result = poller.result()
    return result


def insurance_card_parser(result) -> Dict[str, Any]:
    extracted_info = {}

    for idx, document in enumerate(result.documents):
        doc_type = document.doc_type
        if doc_type:
            extracted_info['DocumentType'] = doc_type

        # Extract Insurer
        insurer = document.fields.get("Insurer")
        if insurer:
            extracted_info['Insurer'] = insurer.value_string

        # Extract Group Number
        group_number = document.fields.get("GroupNumber")
        if group_number:
            extracted_info['GroupNumber'] = group_number.value_string

        # Extract ID Number (and Prefix)
        id_number = document.fields.get("IdNumber")
        if id_number:
            id_info = {}
            number = id_number.value_object.get("Number")
            if number:
                id_info['Number'] = number.value_string
            prefix = id_number.value_object.get("Prefix")
            if prefix:
                id_info['Prefix'] = prefix.value_string
            if id_info:
                extracted_info['IdNumber'] = id_info

        # Extract Member Information
        member = document.fields.get("Member")
        if member:
            member_info = {}
            employer = member.value_object.get("Employer")
            if employer:
                member_info['Employer'] = employer.value_string
            id_suffix = member.value_object.get("IdNumberSuffix")
            if id_suffix:
                member_info['IdNumberSuffix'] = id_suffix.value_string
            name = member.value_object.get("Name")
            if name:
                member_info['Name'] = name.value_string
            if member_info:
                extracted_info['Member'] = member_info

        # Extract Plan Information
        plan = document.fields.get("Plan")
        if plan:
            plan_info = {}
            plan_number = plan.value_object.get("Number")
            if plan_number:
                plan_info['Number'] = plan_number.value_string
            plan_name = plan.value_object.get("Name")
            if plan_name:
                plan_info['Name'] = plan_name.value_string
            if plan_info:
                extracted_info['Plan'] = plan_info

        # Extract Copays
        copays = document.fields.get("Copays")
        if copays:
            copay_info = []
            for copay_idx, copay in enumerate(copays.value_array):
                copay_data = {}
                benefit = copay.value_object.get("Benefit")
                amount = copay.value_object.get("Amount")
                if benefit and amount:
                    copay_data['Benefit'] = benefit.value_string
                    copay_data['Amount'] = amount.value_number
                if copay_data:
                    copay_info.append(copay_data)
            if copay_info:
                extracted_info['Copays'] = copay_info

        # Extract Prescription Info
        prescription_info = document.fields.get("PrescriptionInfo")
        if prescription_info:
            prescription_data = {}
            rx_bin = prescription_info.value_object.get("RxBIN")
            if rx_bin:
                prescription_data['RxBIN'] = rx_bin.value_string
            rx_grp = prescription_info.value_object.get("RxGrp")
            if rx_grp:
                prescription_data['RxGrp'] = rx_grp.value_string
            if prescription_data:
                extracted_info['PrescriptionInfo'] = prescription_data

    return extracted_info


def id_card_parser(result):
    key_value_dict = {}
    for kv_pair in result.key_value_pairs:
        if kv_pair.key and kv_pair.value:
            key_value_dict[kv_pair.key.content] = kv_pair.value.content
        elif kv_pair.key:
            key_value_dict[kv_pair.key.content] = None
        else:
            continue
    return key_value_dict


def analize_doc(blob_add : str, document_type :str) :
    if document_type == "insurance card":
        # Return mock data for insurance card
        return {
            'policy_number': 'POL123456789',
            'insurance_company': 'PT Asuransi Sehat Indonesia',
            'participant_number': 'PA987654321',
            'policy_holder_name': 'BUDI SANTOSO',
            'plan_name': 'Platinum Health'
        }
    elif document_type == "id card":
        try:
            sas_url_dokumen = get_sas_url(blob_add)
            print("Memanggil Document Intelligence...")
            content = get_result(sas_url_dokumen, "prebuilt-layout")
            extracted = id_card_parser(content)
            print("Done Extracting format")
            return extracted
        except Exception as e:
            print(f"ID card processing failed: {e}")
            return {
                'nik': '1234567890123456',
                'full_name': 'BUDI SANTOSO',
                'birth_date': '01-01-1990',
                'gender': 'LAKI-LAKI',
                'marital_status': 'BELUM KAWIN'
            }
    else:
        return {}
