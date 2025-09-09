from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

file_path = "C:\\Users\\Lenovo\\Documents\\project idp\\contoh form insurance\\form-dataset\\output\\form_dokter_1.pdf"
endpoint = os.getenv("AZURE_DOC_INTELLIGENCE_ENDPOINT")
key = os.getenv("AZURE_DOC_INTELLIGENCE_KEY")

def assess_doctor_form_compliance(file_path):
    loader = AzureAIDocumentIntelligenceLoader(
        api_endpoint=endpoint, api_key=key, file_path=file_path, api_model="prebuilt-layout"
    )
    documents = loader.load()
    
    document_text = "\n".join([doc.page_content for doc in documents])
    
    assessment_template = """
    Periksa dokumen doctor form berikut apakah memenuhi semua ketentuan yang diperlukan:

    Dokumen: {document_text}

    KETENTUAN YANG HARUS ADA:
    1. Patient Administrative Data:
       - Admission Date (DD/MM/YYYY)
       - Discharge Date (DD/MM/YYYY)

    2. Doctor-Patient Relationship:
       - Apakah dokter keluarga pasien? (Yes/No + tanggal)
       - Hubungan keluarga dengan pasien? (Yes + jenis hubungan / No)

    3. Diagnosis:
       - Admitting Diagnosis
       - Discharge Diagnosis  
       - Primary Diagnosis + Kode Diagnosis
       - Secondary Diagnosis + Kode (jika ada)

    4. Medical History & Complaints:
       - Penyakit terkait kategori tertentu
       - Keluhan utama dan kronologi
       - Keluhan tambahan
       - Penyakit lain terkait kondisi saat ini
       - Sejak kapan keluhan dialami
       - Pernah mengalami kondisi sama sebelumnya

    5. Referral & Indication:
       - Dirujuk dokter lain? (Yes + nama dokter/RS / No)
       - Indikasi medis rawat inap
       - Diagnosis dapat terjadi dalam waktu singkat?
       - Estimasi sejak kapan keluhan ada

    6. Examination & Treatment:
       - Pemeriksaan fisik dan penunjang
       - Terapi dan jenis prosedur

    7. Doctor Information:
       - Nama dokter
       - SIP (Surat Izin Praktik)
       - Nomor telepon
       - Email
       - Tanggal

    Berikan penilaian:
    KEPUTUSAN: [DISETUJUI/DITOLAK]
    ALASAN: [secara singkat bagian mana yang lengkap jika disetujui dan yang tidak lengkap jika tidak disetujui]
    """
    # KELENGKAPAN: [persentase kelengkapan dari 7 kategori]
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)
    prompt = PromptTemplate(template=assessment_template, input_variables=["document_text"])
    
    result = llm.invoke(prompt.format(document_text=document_text))
    
    return result.content

assessment_result = assess_doctor_form_compliance(file_path)
print(assessment_result)