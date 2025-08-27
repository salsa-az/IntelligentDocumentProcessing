import os
from pydantic import BaseModel, Field
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
import azurefunctions.extensions.bindings.blob as blob
from dotenv import load_dotenv
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import cm
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
from langchain_core.runnables import RunnableParallel, RunnableLambda
from azure.storage.blob import BlobServiceClient
import io 
load_dotenv()
class ClaimEvaluation(BaseModel):
    claim_id: str = Field(..., description="Unique identifier for the claim")
    decision: str = Field(..., description="Either 'Diterima' or 'Ditolak'")
    reason: str = Field(..., description="Explanation for the decision")
    nomor_surat: str = Field(description="Nomor surat resmi")
    nama_pemohon: str = Field(description="Nama orang yang mengajukan")
    tanggal: str = Field(description="Tanggal surat")
    isi_surat: str = Field(description="Isi utama surat persetujuan/penolakan yang bersangkutan, disini hanya perlu ditulis alasan penolakan, saran action, dan informasi lain yg perlu disampaikan. TIDAK PERLU ADA YTH, DENGAN HORMAT ATAUPUN TERIMA KASIH KARNA ITU BUKAN BAGIAN DARI ISI SURAT DIINGINKAN")
    tanda_tangan: str = Field(description="Nama pejabat yang menandatangani")
    customer_email: str = Field(description="Email pelanggan")

# Convert content to text if it's an image
parser = PydanticOutputParser(pydantic_object=ClaimEvaluation)
# Setup Azure OpenAI
"""api_key = os.environ["AZURE_OPENAI_API_KEY"]
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]

    model_name = "gpt-4.1"
    deployment = "gpt-4.1"

    api_version = "2024-12-01-preview"

    llm = AzureChatOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        api_key=api_key,
        model_name=model_name,
        deployment_name=deployment,
    )"""
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
    
    # Create prompt template
template = """
    You are an insurance claim analyst. Based on the following invoice claim details, you will do 3 task : 
    1. check each document data already have each data that he suposed to have. 
    2. Provide your reasoning, for the reason why the claim should be.
    3. create letter of approval/rejection for insurance claim in indonesian language.
    remember that all of this task must be done in sequencial order and consider by data below 
    {document_requirement}

    customer's data : 
    {customer_data}

    customer's doctor Form : 
    {doctor_form_extraction}

    customer's invoice claim : 
    {invoice_claim}

    Please analyze it and return structured output for first task : 
    {format_instructions}

    """
document_requirement = """
Here is the requirement of each document

Doctor form document requirement :

Invoice claim document requirement :
"""
    
prompt = PromptTemplate(
        input_variables=["customer_data", "doctor_form_extraction", "invoice_claim"],
        template=template,
        partial_variables={"format_instructions": parser.get_format_instructions(), "document_requirement": document_requirement},
        )
    
# Create chain
def upload_stream_to_blob(data_stream: io.BytesIO, blob_name: str, connection_string: str, container_name: str) -> str:
    """
    Mengunggah stream data biner ke Azure Blob Storage.
    
    Args:
        data_stream (io.BytesIO): Stream data biner yang akan diunggah.
        blob_name (str): Nama blob (file) di Blob Storage.
        connection_string (str): String koneksi untuk akun penyimpanan Azure.
        container_name (str): Nama kontainer.
    
    Returns:
        str: URL publik dari blob yang diunggah.
    """
    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)
        
        if not container_client.exists():
            container_client.create_container()

        blob_client = container_client.get_blob_client(blob_name)
        
        # Penting: reset posisi stream ke awal sebelum mengunggah
        data_stream.seek(0)
        
        blob_client.upload_blob(data_stream, overwrite=True)
        
        print(f"Stream data '{blob_name}' berhasil diunggah ke Blob Storage.")
        return blob_client.url
        
    except Exception as ex:
        print(f"Terjadi kesalahan saat mengunggah ke Blob Storage: {ex}")
        return None

def generate_pdf(data: ClaimEvaluation):
    print(data)
    print(data.nomor_surat)
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4,
                            rightMargin=3*cm, leftMargin=3*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()

    # Custom styles
    style_normal = styles["Normal"]
    style_normal.fontName = "Times-Roman"
    style_normal.fontSize = 12
    style_normal.leading = 16

    style_center = ParagraphStyle(
        name="Center", parent=style_normal, alignment=TA_CENTER, spaceAfter=20
    )
    style_justify = ParagraphStyle(
        name="Justify", parent=style_normal, alignment=TA_JUSTIFY, spaceAfter=12
    )

    content = []

    # Header nomor & tanggal
    content.append(Paragraph(f"Nomor: {data.nomor_surat}", style_normal))
    content.append(Paragraph(f"Tanggal: {data.tanggal}", style_normal))
    content.append(Spacer(1, 20))

    # Kepada
    content.append(Paragraph("Kepada Yth,", style_normal))
    content.append(Paragraph(data.nama_pemohon, style_normal))
    content.append(Spacer(1, 20))

    # Perihal (rata tengah biar lebih formal)
    content.append(Paragraph(f"<b>Perihal:</b> Persetujuan Klaim Asuransi", style_center))

    # Isi surat (justify)
    isi = f"""
    Dengan hormat,<br/><br/>
    Merujuk pada pengajuan klaim asuransi yang Saudara <b>{data.nama_pemohon}</b> ajukan,
    dengan ini kami memberitahukan bahwa permohonan klaim asuransi Saudara telah
    <b>{data.decision}</b>.<br/><br/>
    {data.isi_surat}<br/><br/>
    Demikian surat pemberitahuan ini kami sampaikan. Atas perhatian dan kerja sama Saudara,
    kami ucapkan terima kasih.
    """
    content.append(Paragraph(isi, style_justify))
    content.append(Spacer(1, 40))

    # Tanda tangan
    content.append(Paragraph("Hormat kami,", style_normal))
    content.append(Spacer(1, 40))
    content.append(Paragraph(f"<b>{data.tanda_tangan}</b>", style_normal))
    connection_string = os.getenv("BLOB_STORAGE_ENDPOINT")
    container_name = "intelegent-document-processing-st"
    # Build PDF
    doc.build(content)
    blob_name = f"Surat_PDF/surat_klaim_{data.claim_id}.pdf"
    blob_url = upload_stream_to_blob(pdf_buffer, blob_name, connection_string, container_name)
    
    # Tutup buffer memori
    pdf_buffer.close()
    return blob_url
# def add_cosmosDB(llmresult : ClaimEvaluation, ) : 

# def send_Gmail(): 
data  = {
    "claim_id": "12345",
    "customer_name": "John Doe",
    "customer_address": "123 Main St, Anytown, USA",
    "customer_email": "johndoe@example.com",
    "customer_phone": "555-1234",
    "ClaimID": "12345",
    "PatientID": "67890",
    "Date" : "26-08-2025", 
    "ProviderID": "54321",
    "ClaimAmount": 1000.00,
    "ClaimDate": "2024-01-01",
    "DiagnosisCode": "OC742",
    "ProcedureCode": "mM276",
    "PatientAge": "72",
    "PatientGender": "M",
    "ProviderSpecialty": "Cardiology",
    "ClaimStatus": "Denied",
    "PatientIncome": "50000",
    "PatientMaritalStatus": "Married",
    "PatientEmploymentStatus": "Employed",
    "ProviderLocation": "Location of the healthcare provider.",
    "ClaimType": "Inpatient",
    "ClaimSubmissionMethod": "Online",
    "Name_approval_officer" : "Jane Smith",
    "customer_email" : "antoyukio17@gmail.com"
}

fullLangchain = prompt | llm | parser | RunnableLambda(generate_pdf)
result = fullLangchain.invoke(input={})
print(result)