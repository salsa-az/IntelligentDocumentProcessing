import os
import base64
from dotenv import load_dotenv
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import cm
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from langchain_community.agent_toolkits import GmailToolkit
from langchain_community.tools.gmail.utils import (
    build_resource_service,
    get_gmail_credentials,
)

load_dotenv()


credentials = get_gmail_credentials(
    token_file="token.json",
    scopes=["https://mail.google.com/"],  # Full Gmail access
    client_secrets_file="credentials.json",
)
api_resource = build_resource_service(credentials=credentials)
toolkit = GmailToolkit(api_resource=api_resource)


# === Step 2: OpenAI LLM Setup ===
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)


# === Schema for Output Parser ===
class ApprovalLetter(BaseModel):
    nomor_surat: str = Field(description="Nomor surat resmi")
    nama_pemohon: str = Field(description="Nama orang yang mengajukan")
    tanggal: str = Field(description="Tanggal surat")
    isi_surat: str = Field(description="Isi utama surat persetujuan")
    tanda_tangan: str = Field(description="Nama pejabat yang menandatangani")

parser = PydanticOutputParser(pydantic_object=ApprovalLetter)


# === Prompt Template ===
template = """
Kamu merupakan seorang asisten yang membuat surat persetujuan/penolakan claim asuransi resmi. 
Tujuan kamu adalah membuat surat persetujuan/penolakan claim asuransi resmi untuk {nama_pemohon}. 
Kamu harus menyesuaikan isi dengan beberapa data berikut: 
- nama : {nama_pemohon}
- tanggal : {tanggal}
- keputusan akhir : {decision}
- alasan atas keputusan : {alasan}
- nama yang menandatangani : {nama_penandatangan}

Output HARUS mengikuti format berikut:
{format_instructions}
"""

prompt = PromptTemplate(
    template=template,
    input_variables=["nama_pemohon", "tanggal", "decision", "alasan", "nama_penandatangan"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

chain = LLMChain(llm=llm, prompt=prompt)


# === PDF Generator ===
def generate_pdf(data: dict, filename="approval_letter.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            rightMargin=3*cm, leftMargin=3*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
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
    content.append(Paragraph(f"Nomor: {data['nomor_surat']}", style_normal))
    content.append(Paragraph(f"Tanggal: {data['tanggal']}", style_normal))
    content.append(Spacer(1, 20))
    content.append(Paragraph("Kepada Yth,", style_normal))
    content.append(Paragraph(data["nama_pemohon"], style_normal))
    content.append(Spacer(1, 20))
    content.append(Paragraph(f"<b>Perihal:</b> Persetujuan Klaim Asuransi", style_center))

    isi = f"""
    Dengan hormat,<br/><br/>
    Merujuk pada pengajuan klaim asuransi yang Saudara <b>{data['nama_pemohon']}</b> ajukan,
    dengan ini kami memberitahukan bahwa permohonan klaim asuransi Saudara telah
    <b>DISETUJUI</b>.<br/><br/>
    {data['isi_surat']}<br/><br/>
    Demikian surat pemberitahuan ini kami sampaikan. Atas perhatian dan kerja sama Saudara,
    kami ucapkan terima kasih.
    """
    content.append(Paragraph(isi, style_justify))
    content.append(Spacer(1, 40))
    content.append(Paragraph("Hormat kami,", style_normal))
    content.append(Spacer(1, 40))
    content.append(Paragraph(f"<b>{data['tanda_tangan']}</b>", style_normal))

    doc.build(content)
    return filename


# === Email Sender (with PDF attachment) ===
def send_email_with_pdf(service, sender, to, subject, body_text, pdf_file):
    """Send email with PDF attachment via Gmail API"""
    message = MIMEMultipart()
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject

    # Attach body text
    message.attach(MIMEText(body_text, "plain"))

    # Attach PDF
    with open(pdf_file, "rb") as f:
        pdf_attachment = MIMEApplication(f.read(), _subtype="pdf")
        pdf_attachment.add_header(
            "Content-Disposition", "attachment", filename=os.path.basename(pdf_file)
        )
        message.attach(pdf_attachment)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    create_message = {"raw": raw_message}

    sent = (
        service.users()
        .messages()
        .send(userId="me", body=create_message)
        .execute()
    )
    print(f"✅ Email sent! Message ID: {sent['id']}")


# === Main Workflow ===
def surat_approval(nama_pemohon, tanggal, decision, alasan, nama_penandatangan):
    print("Memulai pembuatan surat...")
    raw_output = chain.run(
        nama_pemohon=nama_pemohon,
        tanggal=tanggal,
        decision=decision,
        alasan=alasan,
        nama_penandatangan=nama_penandatangan
    )
    parsed = parser.parse(raw_output)
    pdf_file = generate_pdf(parsed.dict(), filename=f"surat_approval_{nama_pemohon.replace(' ', '_')}.pdf")
    print(f"📄 Surat berhasil dibuat: {pdf_file}")

    # Send via email
    send_email_with_pdf(
        service=api_resource,
        sender="me",
        to="antoyukio17@gmail.com",
        subject="Surat Persetujuan Klaim Asuransi",
        body_text=f"Halo {nama_pemohon},\n\nTerlampir surat persetujuan klaim asuransi Anda.\n\nSalam,\n{nama_penandatangan}",
        pdf_file=pdf_file
    )


# === Run ===
print("mulai proses")
surat_approval(
    nama_pemohon="Budi Santoso",
    tanggal="25 Agustus 2025",
    decision="disetujui",
    alasan="Dokumen lengkap dan sesuai ketentuan",
    nama_penandatangan="Dr. Toni"
)
