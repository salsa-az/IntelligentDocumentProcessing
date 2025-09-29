from langchain.tools import tool
import os
from pathlib import Path
from pydantic import BaseModel, Field
from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.agents import initialize_agent, AgentType
from dotenv import load_dotenv
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import cm
from azure.communication.email import EmailClient
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import base64
from azure.storage.blob import BlobServiceClient
from langchain_core.runnables import RunnableLambda
import io 
from azure.cosmos import CosmosClient
import random
from typing import Dict, Any
from dotenv import load_dotenv
from dotenv import load_dotenv
from analyst_tools import cosmos_retrive_data
load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent

pdf_buffer = io.BytesIO()
load_dotenv()
class ClaimLetter(BaseModel):
    nomor_surat: str = Field(description="Number for the letter, which contain SK-(customer_id and claim_id)/type_claim/DDMM/YYYY")
    tanggal: str = Field(description="Date of the letter")
    isi_surat: str = Field(description="Main content of the approval/rejection letter, only needs to include the reason for rejection, suggested action, and other information that needs to be conveyed. DO NOT INCLUDE YTH, DENGAN HORMAT OR TERIMA KASIH AS IT IS NOT PART OF THE DESIRED CONTENT OF THE LETTER")
    tanda_tangan: str = Field(description="Name of the approver")
    customer_email: str = Field(description="Customer email")
    input_data_customer_data : Dict[str, Any] = Field(description="All input data contain the customer data into a single dictionary, not dictionary inside dictionary and the variables name must be the same as the input variable")
    input_data_claim_data : Dict[str, Any] = Field(description="All input data contain the claim data into a single dictionary, not dictionary inside dictionary and the variables name must be the same as the input variable")
    input_data_policy_data : Dict[str, Any] = Field(description="All input data contain the policy data into a single dictionary, not dictionary inside dictionary and the variables name must be the same as the input variable")
    input_data_approval_data : Dict[str, Any] = Field(description="All input data contain the approval data into a single dictionary, not dictionary inside dictionary and the variables name must be the same as the input variable")
    
    
# Create chain

def generate_pdf(data: ClaimLetter) -> str :
    """
    Create the PDF document for the claim letter and automatically upload it to Blob Storage.
    """
    print(data)
    print(data.nomor_surat)
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
    content.append(Paragraph(data.input_data_customer_data["name"], style_normal))
    content.append(Spacer(1, 20))

    # Perihal (rata tengah biar lebih formal)
    content.append(Paragraph(f"<b>Perihal:</b> Persetujuan Klaim Asuransi", style_center))

    # Isi surat (justify)
    isi = f"""
    Dengan hormat,<br/><br/>
    Merujuk pada pengajuan klaim asuransi yang Saudara <b>{data.input_data_customer_data["name"]}</b> ajukan,
    dengan ini kami memberitahukan bahwa permohonan klaim asuransi Saudara telah
    <b>{data.input_data_claim_data["claim_status"]}</b>.<br/><br/>
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
    # Build PDF
    doc.build(content)
    return data
# === Email Sender (with PDF attachment) ===
def send_email_and_upload_pdf(claimletter: ClaimLetter) -> str:
    # --- Build HTML body (same as before) ---
    body = f"""
    <html>
    <body>
        <p>Yth {claimletter.input_data_customer_data['name']},</p>

        <p>Kami ingin memberitahukan bahwa klaim asuransi dengan data:</p>
        <ul>
            <li><b>Claim ID:</b> {claimletter.input_data_claim_data['claim_id']}</li>
            <li><b>Nama Pemohon:</b> {claimletter.input_data_customer_data['name']}</li>
            <li><b>Tanggal Pengajuan:</b> {claimletter.input_data_claim_data['claim_date']}</li>
            <li><b>Jenis Klaim:</b> {claimletter.input_data_claim_data['claim_type']}</li>
        </ul>

        <p>Telah kami proses dan dengan pertimbangan yang matang, kami sampaikan bahwa klaim Anda telah
           <b>{claimletter.input_data_claim_data['claim_status']}</b>.</p>

        <p>Untuk informasi lebih lanjut, Anda dapat memeriksa surat keputusan klaim yang terlampir pada email ini
           atau mengunjungi <a href="{os.getenv('website_kami')}">website kami</a>.</p>

        <p>Terima kasih,<br> {claimletter.tanda_tangan}, <br>Tim Asuransi Anda</p>
    </body>
    </html>
    """

    # --- Prepare attachment from pdf_buffer ---
    pdf_buffer.seek(0)  # make sure we read from the beginning
    pdf_b64 = base64.b64encode(pdf_buffer.read()).decode("utf-8")
    attachment_name = f"surat_klaim_{claimletter.input_data_claim_data['claim_id']}.pdf"

    # --- Send via ACS Email ---
    acs_conn = os.getenv("ACS_EMAIL_CONNECTION_STRING")
    acs_sender = os.getenv("ACS_SENDER_ADDRESS")
    if not acs_conn or not acs_sender:
        raise RuntimeError("ACS_EMAIL_CONNECTION_STRING / ACS_SENDER_ADDRESS is not set.")

    email_client = EmailClient.from_connection_string(acs_conn)

    email_message = {
        "senderAddress": acs_sender,
        "recipients": { "to": [ { "address": claimletter.customer_email } ] },
        "content": {
            "subject": f"Notification of Insurance Claim Decision - {claimletter.input_data_customer_data['name']} - {claimletter.input_data_claim_data['claim_id']}",
            "html": body
        },
        "attachments": [{
            "name": attachment_name,
            "contentType": "application/pdf",
            "contentInBase64": pdf_b64
        }]
    }

    poller = email_client.begin_send(email_message)
    result = poller.result()  # will raise if sending failed
    msg_id = getattr(result, "message_id", None)
    print(f"✅ ACS Email sent! Message ID: {msg_id}")

    # --- Upload the same PDF to Blob ---
    container_name = "intelegent-document-processing-st"
    connection_string = os.getenv("BLOB_STRING_CONNECTION")
    if not connection_string:
        raise RuntimeError("BLOB_STRING_CONNECTION is not set.")

    blob_name = f"Surat_PDF/{attachment_name}"
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    try:
        container_client.create_container()
    except Exception:
        pass  # ignore if already exists

    blob_client = container_client.get_blob_client(blob_name)

    # IMPORTANT: reset buffer AFTER using it for the email attachment
    pdf_buffer.seek(0)
    blob_client.upload_blob(pdf_buffer, overwrite=True)
    print(f"Stream data '{blob_name}' successfully uploaded to Blob Storage.")

    pdf_buffer.close()
    return "Email sent via ACS and PDF uploaded to Blob."

parser_claim_letter = PydanticOutputParser(pydantic_object=ClaimLetter)
llm = AzureChatOpenAI(
    azure_deployment="gpt-4.1",
    temperature=0.4,
)
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
    approver data : 
    {approval_data}
"""

prompt_letter = PromptTemplate(
        input_variables=["customer_data", "claim_data", "policy_data", "approval_data"],
        template=Sys_promt_claim_letter,
        partial_variables={"format_output": parser_claim_letter.get_format_instructions()},
        )
pdf_result = RunnableLambda(generate_pdf)
sendemail = RunnableLambda(send_email_and_upload_pdf)

letter_chain = prompt_letter | llm | parser_claim_letter | pdf_result | sendemail

def letter_chain_pro(customer_id, claim_id,approver_id):
    
    customer_data = cosmos_retrive_data(f"SELECT * FROM c WHERE c.customer_id= @customeridParam", "customer", parameters=[{
        "name" : "@customeridParam",
        "value" : customer_id
    }] )
    print("customer")
    customer_data = customer_data[0]
    claim_data = cosmos_retrive_data(f"SELECT * FROM c WHERE c.claim_id= @idParam", "claim", parameters=[{
        "name" : "@idParam",
        "value" : claim_id
    }] )
    print("claim")
    claim_data = claim_data[0]
    policy_data = cosmos_retrive_data(f"SELECT * FROM c WHERE c.policy_id= @idParam", "policy", parameters=[{
        "name" : "@idParam",
        "value" : claim_data["policy_id"]
    }] )
    policy_data = policy_data[0]
    print("policy")
    approver_data = cosmos_retrive_data(f"SELECT * FROM c WHERE c.admin_id= @idParam", "insurance_admin", parameters=[{
        "name" : "@idParam",
        "value" : approver_id
    }] )
    approver_data = approver_data[0]
    print("approver")
    
    return letter_chain.invoke({
        "customer_data": customer_data,
        "claim_data": claim_data,
        "policy_data": policy_data,
        "approval_data": approver_data
    })