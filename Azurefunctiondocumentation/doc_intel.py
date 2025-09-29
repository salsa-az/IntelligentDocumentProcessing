import json
import re
import os
from datetime import datetime, timedelta,timezone 
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
from azure.ai.formrecognizer import DocumentAnalysisClient
from dotenv import load_dotenv

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

def clean_all_content(all_content: dict, top_field_values: list):
    cleaned_pages = {}
    top_tokens = [re.sub(r'\s+', '', str(tv)).lower() for tv in top_field_values if isinstance(tv, str)]
    for page_idx, page in all_content.items():
        lines = page.get('lines', [])
        cleaned_lines = []
        for line in lines:
            if not isinstance(line, str):
                continue
            l = line.replace('\n', ' ').strip()
            l = re.sub(r'\s+', ' ', l)
            if not l:
                continue
            if re.fullmatch(r'\d+', l):
                continue
            if re.fullmatch(r'^[\W_]+$', l):
                continue
            l_token = re.sub(r'\s+', '', l).lower()
            skip = False
            for tk in top_tokens:
                if l_token == tk or l_token in tk or tk in l_token:
                    skip = True
                    break
            if skip:
                continue
            if 'nip' in l.lower():
                digits = re.sub(r'\D', '', l)
                if digits:
                    l = f'NIP : {digits}'
            l = re.sub(r'\s*([.,()])\s*', r'\1 ', l).strip()
            l = re.sub(r'\s*:\s*$', '', l)
            cleaned_lines.append(l)
        deduped = []
        for item in cleaned_lines:
            if not deduped or item != deduped[-1]:
                deduped.append(item)
        full_text = ' '.join(deduped).strip()
        cleaned_pages[page_idx] = {
            'cleaned_lines': deduped,
            'full_text': full_text
        }
    return cleaned_pages

def clean_document(data: dict):
    top_fields = {}
    for k, v in data.items():
        if k == 'All content':
            continue
        nk = normalize_key(k, keep_colon=False)
        top_fields[nk] = clean_simple_value(nk, v) if isinstance(v, str) else v
    top_vals = list(top_fields.values())
    allc = data.get('All content', {})
    cleaned_all = clean_all_content(allc, top_vals)
    return {
        'fields': top_fields,
        'all_content': cleaned_all
    }

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

def invoice_parser(invoices) : 
    invoice_data = {}
    for idx, invoice in enumerate(invoices.documents):
        invoice_info = {}
        # Vendor Information
        vendor_name = invoice.fields.get("VendorName")
        if vendor_name:
            invoice_info["Vendor Name"] = str(vendor_name.value_string)
        
        vendor_address = invoice.fields.get("VendorAddress")
        if vendor_address:
            invoice_info["Vendor Address"] = str(vendor_address.value_address)
        
        vendor_address_recipient = invoice.fields.get("VendorAddressRecipient")
        if vendor_address_recipient:
            invoice_info["Vendor Address Recipient"] = str(vendor_address_recipient.value_string)
        
        # Customer Information
        customer_name = invoice.fields.get("CustomerName")
        if customer_name:
            invoice_info["Customer Name"] = str( customer_name.value_string)
        customer_id = invoice.fields.get("CustomerId")
        if customer_id:
            invoice_info["Customer Id"] =str(customer_id.value_string)

        customer_address = invoice.fields.get("CustomerAddress")
        if customer_address:
            invoice_info["Customer Address"] = str(customer_address.value_address)

        customer_address_recipient = invoice.fields.get("CustomerAddressRecipient")
        if customer_address_recipient:
            invoice_info["Customer Address Recipient"] = str(customer_address_recipient.value_string
)
        # Invoice Details
        invoice_id = invoice.fields.get("InvoiceId")
        if invoice_id:
            invoice_info["Invoice Id"] = str(invoice_id.value_string)

        invoice_date = invoice.fields.get("InvoiceDate")
        if invoice_date:
            invoice_info["Invoice Date"] = str(invoice_date.value_date)

        invoice_total = invoice.fields.get("InvoiceTotal")
        if invoice_total:
            invoice_info["Invoice Total"] = str(invoice_total.value_currency.amount)
        due_date = invoice.fields.get("DueDate")
        if due_date:
            invoice_info["Due Date"] = str(due_date.value_date)

        purchase_order = invoice.fields.get("PurchaseOrder")
        if purchase_order:
            invoice_info["Purchase Order"] = str(purchase_order.value_string)

        # Billing and Shipping Information
        billing_address = invoice.fields.get("BillingAddress")
        if billing_address:
            invoice_info["Billing Address"] = str(billing_address.value_address)

        billing_address_recipient = invoice.fields.get("BillingAddressRecipient")
        if billing_address_recipient:
            invoice_info["Billing Address Recipient"] = str(billing_address_recipient.value_string)

        shipping_address = invoice.fields.get("ShippingAddress")
        if shipping_address:
            invoice_info["Shipping Address"] = str(shipping_address.value_address)

        shipping_address_recipient = invoice.fields.get("ShippingAddressRecipient")
        if shipping_address_recipient:
            invoice_info["Shipping Address Recipient"] = str(shipping_address_recipient.value_string)

        # Items Information
        items_info = []
        for item_idx, item in enumerate(invoice.fields.get("Items").value_array):
            item_info = {}
            item_description = item.value_object.get("Description")
            if item_description:
                item_info["Description"] = str(item_description.value_string)
            
            item_quantity = item.value_object.get("Quantity")
            if item_quantity:
                item_info["Quantity"] = str(item_quantity.value_number)
            
            unit = item.value_object.get("Unit")
            if unit:
                item_info["Unit"] = str(unit.value_number)
            
            unit_price = item.value_object.get("UnitPrice")
            if unit_price:
                item_info["Unit Price"] = str(unit_price.value_currency.amount)

            product_code = item.value_object.get("ProductCode")
            if product_code:
                item_info["Product Code"] = str(product_code.value_string)

            item_date = item.value_object.get("Date")
            if item_date:
                item_info["Date"] = str(item_date.value_date)

            tax = item.value_object.get("Tax")
            if tax:
                item_info["Tax"] = str(tax.value_string)

            amount = item.value_object.get("Amount")
            if amount:
                item_info["Amount"] = str(amount.value_currency.amount)
            
            items_info.append(item_info)
        
        invoice_info["Items"] = items_info
        
        # Additional Fields
        subtotal = invoice.fields.get("SubTotal")
        if subtotal:
            invoice_info["Subtotal"] = str(subtotal.value_currency.amount)

        total_tax = invoice.fields.get("TotalTax")
        if total_tax:
            invoice_info["Total Tax"] = str(total_tax.value_currency.amount)

        previous_unpaid_balance = invoice.fields.get("PreviousUnpaidBalance")
        if previous_unpaid_balance:
            invoice_info["Previous Unpaid Balance"] = str(previous_unpaid_balance.value_currency.amount)

        amount_due = invoice.fields.get("AmountDue")
        if amount_due:
            invoice_info["Amount Due"] = str(amount_due.value_currency.amount)

        service_start_date = invoice.fields.get("ServiceStartDate")
        if service_start_date:
            invoice_info["Service Start Date"] = str(service_start_date.value_date)

        service_end_date = invoice.fields.get("ServiceEndDate")
        if service_end_date:
            invoice_info["Service End Date"] = str(service_end_date.value_date)

        service_address = invoice.fields.get("ServiceAddress")
        if service_address:
            invoice_info["Service Address"] = str(service_address.value_address)

        service_address_recipient = invoice.fields.get("ServiceAddressRecipient")
        if service_address_recipient:
            invoice_info["Service Address Recipient"] = str(service_address_recipient.value_string
)
        remittance_address = invoice.fields.get("RemittanceAddress")
        if remittance_address:
            invoice_info["Remittance Address"] = str(remittance_address.value_address)

        remittance_address_recipient = invoice.fields.get("RemittanceAddressRecipient")
        if remittance_address_recipient:
            invoice_info["Remittance Address Recipient"] = str(remittance_address_recipient.value_string)

        invoice_data["Invoice #{}".format(idx + 1)] = invoice_info 
    return invoice_data

def doctor_form_parser(result):
    out = {}
    # -------- Documents --------
    for document in getattr(result, "documents", []) or []:
        doc_entry = {
            "doc_type": getattr(document, "doc_type", None),
            "fields": {},            # { field_name: {type, value, (confidence?)} }
            "flat_fields": {},       # { field_name: value } -> memudahkan akses cepat
        }

        fields = getattr(document, "fields", {}) or {}
        for name, field in fields.items():
            f_val  = getattr(field, "content", None)
            out[name] = str(f_val)
    return out


def report_lab_parser(result) : 
    out = {}
    for idx, document in enumerate(result.documents):
        for name, field in document.fields.items():
            if name == "Result test" : 
                table = field.value_array
                table_data = []
                for item in table:
                    item_data = {}
                    for sub_name, sub_field in item.value_object.items():
                        item_data[sub_name] = str(sub_field.content)
                    table_data.append(item_data)
                out[idx][name] = table_data
            else :
                out[idx][name]= str(field.content)
    return out 

def general_doc_parser(result) :
    all_result = {}
    extracted_data = {}
    for kv_pair in result.key_value_pairs:
        if kv_pair.key and kv_pair.value:
            all_result[kv_pair.key.content] = kv_pair.value.content
        else:
            all_result[kv_pair.key.content] = "-"
    # Iterate over each page in the result
    for page in result.pages:
        page_number = page.page_number
        extracted_data[page_number] = {
            "lines": [],
            "selection_marks": [],
            "tables": []
        }

        # Extract lines content from the page
        for line in page.lines:
            extracted_data[page_number]["lines"].append(line.content)

        # Extract selection marks content (state of the mark)
        for selection_mark in page.selection_marks:
            extracted_data[page_number]["selection_marks"].append(selection_mark.state)

    # Extract table layout and content
    for table_idx, table in enumerate(result.tables):
        for region in table.bounding_regions:
            page_number = region.page_number
            table_data = []

            for cell in table.cells:
                # Organize cell content by row and column
                if cell.row_index >= len(table_data):
                    table_data.append([None] * table.column_count)
                table_data[cell.row_index][cell.column_index] = cell.content

            # Store table layout (rows and columns) content
            extracted_data.setdefault(page_number, {"tables": []})["tables"].append({
                "table_index": table_idx,
                "rows": table.row_count,
                "columns": table.column_count,
                "content": table_data
            })
    all_result = clean_document(all_result)
    all_result["All content"] = extracted_data
    return all_result
def get_result(sas_url_dokumen, model_name) :
    print(f"Memproses dokumen dengan model: {model_name}")
    if model_name == "prebuilt-document" :
        poller = document_analysis_client.begin_analyze_document_from_url("prebuilt-document", sas_url_dokumen)
        result = poller.result()    
    else : 
        poller = document_intelligence_client.begin_analyze_document(
            model_id=model_name,
            body=AnalyzeDocumentRequest(url_source=sas_url_dokumen)
        )
        result = poller.result()
    return result

def analize_doc(blob_add : str, document_type :str) :
    sas_url_dokumen = get_sas_url(blob_add)
    print("Memanggil Document Intelligence...")
    if  document_type == "invoice" :
        result_doc = get_result(sas_url_dokumen, "prebuilt-invoice")
        extracted = invoice_parser(result_doc)
    elif document_type == "doctor form" :
        result_doc = get_result(sas_url_dokumen, "form_doctor")
        extracted = doctor_form_parser(result_doc) 
    elif document_type == "report lab" :
        result_doc = get_result(sas_url_dokumen, "report_lab")
        extracted = doctor_form_parser(result_doc) 
    elif document_type == "additional document" :
        result_doc = get_result(sas_url_dokumen, "prebuilt-document")
        extracted = general_doc_parser(result_doc)
    print("Done Extracting format")
    return extracted