import os
import base64
from dotenv import load_dotenv
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import cm
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from googleapiclient.discovery import build
from google.oauth2 import service_account
load_dotenv()

class ApprovalLetter(BaseModel):
    nomor_surat: str = Field(description="Nomor surat resmi")
    nama_pemohon: str = Field(description="Nama orang yang mengajukan")
    tanggal: str = Field(description="Tanggal surat")
    isi_surat: str = Field(description="Isi utama surat persetujuan")
    tanda_tangan: str = Field(description="Nama pejabat yang menandatangani")
parser = PydanticOutputParser(pydantic_object=ApprovalLetter)

template = """
Kamu merupakan seorang asisten yang membuat surat surat persetujuan/penolakan claim asuransi resmi. 
tujuan kamu adalah membuat surat persetujuan persetujuan/penolakan claim asuransi resmi untuk {nama_pemohon} 
kamu harus menyesuaikan isi dengan beberapa data berikut : 
nama : {nama_pemohon}
tanggal : {tanggal}
keputusan akhir : {decision}
Alasan atas keputusan : {alasan}
Nama yang menandatangani : {nama_penandatangan}
ingatlah bahwa kamu melakukan ini atas dasar keputusan yang diberikan sehingga surat yang nanti kamu buat harus sesuai dengan data dan keputusan yang telah diberikan.
INGAT KALAU OUTPUT YANG AKAN KAMU BERIKAN SEPERTI BERIKUT : 
{format_instructions}
"""
prompt = PromptTemplate(
    template=template,
    input_variables=["nama_pemohon",'tanggal', "decision", 'alasan', "nama_penandatangan"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
chain = LLMChain(llm=llm, prompt=prompt)

def generate_pdf(data: dict, filename="approval_letter.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=A4,
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
    content.append(Paragraph(f"Nomor: {data['nomor_surat']}", style_normal))
    content.append(Paragraph(f"Tanggal: {data['tanggal']}", style_normal))
    content.append(Spacer(1, 20))

    # Kepada
    content.append(Paragraph("Kepada Yth,", style_normal))
    content.append(Paragraph(data["nama_pemohon"], style_normal))
    content.append(Spacer(1, 20))

    # Perihal (rata tengah biar lebih formal)
    content.append(Paragraph(f"<b>Perihal:</b> Persetujuan Klaim Asuransi", style_center))

    # Isi surat (justify)
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

    # Tanda tangan
    content.append(Paragraph("Hormat kami,", style_normal))
    content.append(Spacer(1, 40))
    content.append(Paragraph(f"<b>{data['tanda_tangan']}</b>", style_normal))

    # Build PDF
    doc.build(content)
    return filename

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

print("mulai proses")
surat_approval(
    nama_pemohon="Budi Santoso",
    tanggal="25 Agustus 2025",
    decision="disetujui",
    alasan="Dokumen lengkap dan sesuai ketentuan",
    nama_penandatangan="Dr. Toni"
)