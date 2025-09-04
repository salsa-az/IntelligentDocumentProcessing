from langchain.tools import tool
import os
from pydantic import BaseModel, Field
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.agents import initialize_agent, AgentType
import azurefunctions.extensions.bindings.blob as blob
from dotenv import load_dotenv
import json
from pyparsing import Dict
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
from azure.storage.blob import BlobServiceClient
from langchain_core.runnables import RunnableParallel, RunnableLambda
import io 
from azure.cosmos import CosmosClient
import random
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_google_community import GmailToolkit
from langchain_google_community.gmail.utils import (
    build_resource_service,
    get_gmail_credentials,
)
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
credentials = get_gmail_credentials(
    token_file="token.json",
    scopes=["https://mail.google.com/"],
    client_secrets_file="credentials.json",
)
toolkit = GmailToolkit()
api_resource = build_resource_service(credentials=credentials)
load_dotenv()
class ClaimLetter(BaseModel):
    claim_id: str = Field(..., description="Unique identifier for the claim")
    decision: str = Field(..., description="Either 'Diterima' or 'Ditolak'")
    reason: str = Field(..., description="Explanation for the decision")
    nomor_surat: str = Field(description="Number for the letter, which contain SK-(customer_id and claim_id)/type_claim/DDMM/YYYY")
    nama_pemohon: str = Field(description="Name of the applicant")
    tanggal: str = Field(description="Date of the letter")
    isi_surat: str = Field(description="Main content of the approval/rejection letter, only needs to include the reason for rejection, suggested action, and other information that needs to be conveyed. DO NOT INCLUDE YTH, DENGAN HORMAT OR TERIMA KASIH AS IT IS NOT PART OF THE DESIRED CONTENT OF THE LETTER")
    tanda_tangan: str = Field(description="Name of the signing official")
    customer_email: str = Field(description="Customer email")
    subject_email: str = Field(description="Email subject")
    body_email: str = Field(description="Email body. it compact and informative but not too short and too long")

# Create chain
def upload_stream_to_blob(data_stream: io.BytesIO, blob_name: str, connection_string: str, container_name: str) -> str:
    
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
# === Email Sender (with PDF attachment) ===
def send_email(claimletter : ClaimLetter) -> str:
    """Send email Gmail API"""
    message = MIMEMultipart()
    message["to"] = claimletter.customer_email
    message["from"] = "me"
    message["subject"] = claimletter.subject_email

    # Attach body text
    message.attach(MIMEText(claimletter.body_email, "plain"))

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    create_message = {"raw": raw_message}

    sent = (
        api_resource.users()
        .messages()
        .send(userId="me", body=create_message)
        .execute()
    )
    print(f"✅ Email sent! Message ID: {sent['id']}")

def generate_pdf(data: ClaimLetter) -> str :
    """
    Create the PDF document for the claim letter and automatically upload it to Blob Storage.
    """
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

parser_claim_letter = PydanticOutputParser(pydantic_object=ClaimLetter)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
Sys_promt_claim_letter = """
    You are an insurance claim secretary. Based on the following invoice claim details, you will do 3 task : 
    1. prepare to make the claim letter with give every tool what they need to create the letter
    2. you will create the claim letter using tool generate_pdf, with this tool you will automaticaly upload to the blob storage
    3. you will send a notification email for notify claimer's claim status, by using send_email.
    RULE : 
    1. USE FORMAL LANGUAGE
    2. USE INDONESIAN LANGUAGE
    3. USE THE INPUT FORMAT AND DON'T DEVIATE
    HERE INPIT FORMAT 
    {format_output}

    Policy data : 
    {policy_data}
    
    claimer data : 
    {customer_data}

    claim data : 
    {claim_data}
"""

prompt_letter = PromptTemplate(
        input_variables=["customer_data", "claim_data", "policy_data"],
        template=Sys_promt_claim_letter,
        partial_variables={"format_output": parser_claim_letter.get_format_instructions()},
        )

parallel_process = RunnableParallel(
    pdf_result=RunnableLambda(generate_pdf),
    sendemail=RunnableLambda(send_email)
)
letter_chain = prompt_letter | llm | parser_claim_letter | parallel_process

def letter_chain_pro(customer_data, claim_data, policy_data):
    return letter_chain.invoke({
        "customer_data": customer_data,
        "claim_data": claim_data,
        "policy_data": policy_data
    })