import os
import json
import io 
import random
from typing import List, Dict, Any, Optional
import re
import requests 

# Azure Libs
from azure.cosmos import CosmosClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

# Langchain Libs
from langchain.tools import tool, Tool
from pydantic import BaseModel, Field
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.agents import initialize_agent, AgentType
from langchain_community.utilities import SerpAPIWrapper
from langchain_google_community import GmailToolkit
from langchain_google_community.gmail.utils import (
    build_resource_service,
    get_gmail_credentials,
)
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
load_dotenv()

class ClaimSuggestion(BaseModel):
    claim_id: str = Field(..., description="Unique identifier for the claim")
    decision: str = Field(..., description="the final Suggestion, the only option is Approved/Rejected/Pending. DO NOT GIVE ANY OTHER STATUS AND EXPLANATION")
    reasoning: str = Field(..., description="Explanation for the suggestion")
    summary: str = Field(description="Summary of the claim, just pass the summary from the input")
    input_customer_data: dict = Field(description="data mentah customer data diinputkan")
    input_claim_data: dict = Field(description="data mentah claim detail yang diinputkan")
    input_document_invoice_data: dict = Field(description="data mentah invoice yang diinputkan")
    input_document_doctorform_data: dict = Field(description="data mentah doctor data yang diinputkan")

class ClaimEvaluation(BaseModel):
    claim_id: str = Field(..., description="Unique identifier for the claim")
    validation: str = Field(..., description="is the claim valid or not, the only option is Valid/Not Valid. DO NOT GIVE ANY OTHER STATUS AND EXPLANATION")
    Claim_summary: str = Field(description="Summary of the claim")
    input_customer_data: dict = Field(description="data mentah customer data diinputkan")
    input_claim_data: dict = Field(description="data mentah claim detail yang diinputkan")
    input_document_invoice_data: dict = Field(description="data mentah invoice yang diinputkan")
    input_document_doctorform_data: dict = Field(description="data mentah doctor data yang diinputkan")

cosmos_db_uri = os.getenv("COSMOS_DB_URI")
cosmos_db_key = os.getenv("COSMOS_DB_KEY")
database_name = os.getenv("COSMOS_DB_DATABASE_NAME")

client = CosmosClient(cosmos_db_uri, credential=cosmos_db_key)
database = client.get_database_client(database_name)

class QueryInput(BaseModel):
    query: str = Field(..., description="Cosmos SQL query, example: SELECT TOP 5 c.id, c.name FROM c")
    container : str = Field(..., description="name container in Cosmos DB")
    parameters: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Opsional. List [{'name':'@param','value':..}] untuk query"
    )

@tool("get_DB_details")
def get_db_details() -> str:
    """get the metadata of the Cosmos DB"""
    details = f"""
    here is the format of the Cosmos DB: 
    {'-'*5} item in database {'-'*5}
    container :
    1. "document" : container where all the document's detail is stored
    PK: "doc_id" : unique identifier for each document
    FK: "claim_id"
    Attributes:
        "doc_type" : determine the type of document ( invoice, Doctor form)
        "document_content" : the actual content of the document (contain of extracted document from pdf)
    2. "claim" : 
    PK: "claim_id" : unique identifier for each claim
    FKs:
        "customer_id"
        "admin_id"
    Attributes:
        "claim_type" : type of claim (e.g. rawat nginap)
        "claim_amount" : total of claim
        "claim_date" : time of claim issue 
        "documents" : list of documents related to the claim
        "claim_form" : 
        "claim_status" : claim status that were given by the INSURANCE CLAIM OFFICER APPROVAL (the only option are "Approved", "Rejected", "Pending", "Prosses") YOU SHOULD LEAVE THIS EMPTY
        "claim_reason" :  claim status reason why were accepted/rejected by INSURANCE CLAIM OFFICER APPROVAL YOU SHOULD LEAVE THIS EMPTY 
        "summary" : the summary of the claim 
        "AI_suggestion" : the suggestion by system for the claim by AI Agent
        "AI_reasoning" : the reasoning behind the system's suggestion by AI Agent

    3. "customer"
    PK: "customer_id" : unique identifier for each customer
    FK: "policy_id"
    Attributes:
        "customer_no" : the customer number
        "name" : the name of the customer
        "dob" : the date of birth
        "age" : the age
        "gender" : the gender
        "NIK" : the national identification number
        "email" : the email address
        "is_policy_holder" : whether the customer is the policy holder
        "relation_with_policy_holder" : the relationship with the policy holder
        "employment_status" : the employment status
        "marital_status" : the marital status
        "income" : the income
        "claim_history" : the history of claims made by the customer 

    4. "policy"
    PK: "policy_id" : unique identifier for each policy
    FK: "user_id"
    Attributes:
        "policy_no" : the policy number
        "policyholder_name" : the name of the policyholder
        "insured_name" : the name of the insured
        "start_date" : the start date of the policy
        "expire_date" : the expiration date of the policy
        "insurance_plan_type" : the type of insurance plan
        "total_claim_limit" : the total claim limit for the policy

    5. "Insurance Administrator"
    PK: "admin_id" : unique identifier for each insurance administrator
    Attributes:
        "username" : the username of the insurance administrator
        "email" : the email address of the insurance administrator

    {'-'*5} Relationships {'-'*5}
    Documents → Claim: Many-to-One (claim_id)
    Claim → Customer: Many-to-One (customer_id)
    Claim → Insurance Administrator: Many-to-One (admin_id)
    Customer → Policy: Many-to-One (policy_id)
    Policy → Customer: One-to-Many (reverse relation)
    """
    return details

@tool("cosmos_select")
def cosmos_select_tool(query: str, container: str, parameters: list = None) -> List[Dict[str, Any]]:
    """Run a Cosmos DB select query."""
    try:
        container_client = database.get_container_client(container)
        items = list(container_client.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        print(f"Query executed successfully. Retrieved {len(items)} items.")
        return items
    except Exception as e:
       print(f"Error querying Cosmos DB: {e}")
       return []

search = SerpAPIWrapper()
search_tool = Tool(
    name="web search",
    description="Search the web for information, useful for when you need to find current information or look up specific details online.(e.g. berapa harga rata-rata pengobatan untuk penyakit X di Indonesia?)",
    func=search.run,
)

@tool("get_disease_info")
def get_disease_info(search_key, min_score=0.5):
    """search for disease information from WHO ICD API, to verify the diagnosa"""
    token_endpoint = 'https://icdaccessmanagement.who.int/connect/token'
    client_id = 'ef108bbc-154c-401a-b7ba-15758a60c878_1bd261be-3e0f-495a-ae9d-1f8c0967ed04'
    client_secret = '2gmDnJPBN5CxYl8HxOgS720MtPTWyIb3M0az0Kf/bUI='
    scope = 'icdapi_access'
    grant_type = 'client_credentials'
    
    payload = {'client_id': client_id, 
            'client_secret': client_secret, 
            'scope': scope, 
            'grant_type': grant_type}
            
    r = requests.post(token_endpoint, data=payload, verify=False).json()
    token = r['access_token']

    headers = {'Authorization':  'Bearer '+token, 
            'Accept': 'application/json', 
            'Accept-Language': 'en',
        'API-Version': 'v2'}
    uri = f'https://id.who.int/icd/entity/search?q={search_key}'

    searchData = requests.get(uri, headers=headers, verify=False)
    searchData = searchData.json()
    finalData = {}
    
    if "destinationEntities" in searchData and isinstance(searchData["destinationEntities"], list):
        for i, entity in enumerate(searchData["destinationEntities"]):
            score = entity.get("score", 0)
            if score >= min_score:
                title = entity.get("title", "Tidak tersedia").replace("<em>", "").replace("</em>", "")
                entity_id = entity.get("id", "Tidak tersedia")
                score = entity.get("score", "Tidak tersedia")
                response = requests.get(entity_id, headers=headers, verify=False)
                response.raise_for_status()
                response = response.json()
                detail = response.get('definition') 
                if detail:
                    detail = detail.get('@value', 'Tidak tersedia')
                else:
                    detail = "Tidak tersedia"
                finalData[i] = {
                        "title": title.replace("<em class='found'>", "").replace("</em>", ""),
                        "id": entity_id,
                        "score": score,
                        "details": detail
                }
    return finalData

@tool('update_claim_with_ai_decision')
def update_claim_with_ai_decision(claim_id: str, ai_suggestion: str, ai_reasoning: str, summary: str) -> str:
    """Update existing claim with AI suggestion and reasoning"""
    try:
        container_client = database.get_container_client("claim")
        
        # Get existing claim
        existing_claims = list(container_client.query_items(
            query=f"SELECT * FROM c WHERE c.claim_id = '{claim_id}'",
            enable_cross_partition_query=True
        ))
        
        if not existing_claims:
            return f"Claim {claim_id} not found"
        
        claim = existing_claims[0]
        claim['AI_suggestion'] = ai_suggestion
        claim['AI_reasoning'] = ai_reasoning
        claim['summary'] = summary
        
        container_client.upsert_item(claim)
        print(f'Successfully updated claim {claim_id} with AI decision')
        return "done"
    except Exception as e:
        return f"Error updating claim: {e}"

# Azure Document Intelligence setup
AZURE_DOC_INTELLIGENCE_ENDPOINT = os.getenv("AZURE_DOC_INTELLIGENCE_ENDPOINT")
AZURE_DOC_INTELLIGENCE_KEY = os.getenv("AZURE_DOC_INTELLIGENCE_KEY")
CUSTOM_MODEL_ID = os.getenv("CUSTOM_MODEL_ID")

document_intelligence_client = DocumentIntelligenceClient(
    endpoint=AZURE_DOC_INTELLIGENCE_ENDPOINT,
    credential=AzureKeyCredential(AZURE_DOC_INTELLIGENCE_KEY)
)

from azure.storage.blob import BlobServiceClient

def get_blob_content(blob_url: str) -> bytes:
    """Download blob content using connection string"""
    try:
        conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if conn_str:
            blob_service = BlobServiceClient.from_connection_string(conn_str)
            url_parts = blob_url.replace('%20', ' ').split('/')
            container_name = url_parts[3]
            blob_name = '/'.join(url_parts[4:])
            blob_client = blob_service.get_blob_client(container=container_name, blob=blob_name)
            return blob_client.download_blob().readall()
        return None
    except Exception as e:
        print(f"Blob download error: {e}")
        return None

def extract_doctor_form(blob_url: str) -> dict:
    """Extract doctor form using Azure Document Intelligence custom model"""
    try:
        blob_content = get_blob_content(blob_url)
        if not blob_content:
            return {"error": "Failed to download blob"}
        
        poller = document_intelligence_client.begin_analyze_document(
            CUSTOM_MODEL_ID,
            AnalyzeDocumentRequest(bytes_source=blob_content)
        )
        result = poller.result()
        
        extracted_fields = {}
        if result.documents:
            for document in result.documents:
                for name, field in document.fields.items():
                    extracted_fields[name] = {
                        "content": field.content,
                        "confidence": field.confidence
                    }
        
        return extracted_fields
    except Exception as e:
        return {"error": str(e)}

def extract_invoice(blob_url: str) -> dict:
    """Extract invoice using prebuilt-invoice model"""
    try:
        blob_content = get_blob_content(blob_url)
        if not blob_content:
            return {"error": "Failed to download blob"}
        
        poller = document_intelligence_client.begin_analyze_document(
            "prebuilt-invoice",
            AnalyzeDocumentRequest(bytes_source=blob_content)
        )
        result = poller.result()
        
        extracted_fields = {}
        if result.documents:
            for document in result.documents:
                for name, field in document.fields.items():
                    extracted_fields[name] = {
                        "content": field.content,
                        "confidence": field.confidence
                    }
        
        return extracted_fields
    except Exception as e:
        return {"error": str(e)}

parser_claim_analyst = PydanticOutputParser(pydantic_object=ClaimEvaluation)
document_requirement = """
    Here is the requirement of each document

    Doctor form document requirement :
        Note: The requirements listed below may or may not be written in the same order as they appear in the document. Please ensure all required information is present, regardless of order.
        Doctor form document requirement :
        1. Patient Administrative Data
            - Admission Date - Format: DD/MM/YYYY
            - Discharge Date - Format: DD/MM/YYYY

        2. Doctor-Patient Relationship (Which is filled by choosing one of the options in the checkbox)
            - Are you the patient's family doctor? (Yes/No + date if Yes)  
            - Do you have a family relationship with the patient? (Yes + type of relationship / No)  

        3. Diagnosis
            - Admitting Diagnosis  
            - Discharge Diagnosis  
            - Primary Diagnosis and Diagnosis Code
            - Secondary Diagnosis and Diagnosis Code (If needed)
            
        4. Medical History & Complaints
            - Disease related to:  
            (cosmetic / pregnancy / fertility / psychiatric / congenital disorder / growth & development disorder / fertility treatment / drug abuse / sexually transmitted disease / HIV AIDS / Other)  
            - Main complaint and chronology  
            - Additional complaints  
            - Are there any other diseases/complaints related to the current condition? (If yes, specify and since when)  
            - Since when has the patient experienced these complaints/symptoms?  
            - Has the patient experienced the same condition before the treatment date? (Yes + date / No)  

        5. Referral & Indication for Hospitalization
            - Is the patient referred by another doctor? (Yes + doctor's name or hospital or clinic / No)  
            - If hospitalization is required, what is the medical indication?  
            - Can the diagnosis occur in a short period of time? (Doctor's opinion based on medical literature and professional experience)  
            - Since when is the complaint estimated to have existed? (Estimated duration in months)  

        6. Examination & Treatment
            - Physical and supporting examinations  
            - Therapy and type of procedure

        7. Treating Doctor's Information
            - Doctor's name  
            - Doctor's Practice License (SIP)  
            - Phone number  
            - Email  
            - Signature and stamp  
            - Date

    Invoice claim document requirement :
        Invoice claim document requirement (General Hospital Invoice):
        1. Invoice Number
        2. Invoice Date
        3. Patient Name
        4. Date(s) of Service or Hospitalization
        6. Itemized List of Charges (each service/procedure with cost)
        7. Total Amount Due
        8. Currency
        9. Hospital/Provider Name
        11. Hospital/Provider Address
        12. Hospital/Provider Contact Information
        14. Payment Instructions or Method
"""

Sys_promt_claim_analysis = """ You are an insurance claim addministrator. Based on the following invoice claim details, you will do 4 task : 
    1. check each document data already have each data that he suposed to have. please ensure that all required fields are present, give the validation. The requirement is as follows:
    {document_requirement}

    2. create a summary of the claim, and pass the result to the summary field.
    3. finally give the output in the form of JSON format as follows :
    {format_output}
    RULES:
    1. USE FORMAL LANGUAGE
    2. USE INDONESIAN LANGUAGE

    claimer data : 
    {customer_data}

    claim data : 
    {claim_data}

    doctor form : 
    {doctor_form_extraction}

    invoice Form : 
    {invoice_claim}
    """

prompt_analyst = PromptTemplate(
        input_variables=["customer_data", "doctor_form_extraction", "invoice_claim", "claim_data"],
        template=Sys_promt_claim_analysis,
        partial_variables={"format_output": parser_claim_analyst.get_format_instructions(), "document_requirement": document_requirement},
        )

parser_claim_decision = PydanticOutputParser(pydantic_object=ClaimSuggestion)

system_prompt = F"""
    You are an insurance claims assistant. Your purpose is to provide a claim recommendation—whether it should be **Approved**, **Rejected**, or **Pending**—based on the data provided.

    YOU MUST FOLLOW THIS PROCESS BEFORE GIVING THE RECOMMENDATION:

    1.  **Initial Validation**: Check the validation status from the input. If the status is "NOT VALID", proceed directly to **Step 6**. If the status is "VALID", continue to the next step.

    2.  **Duplicate Claim Check**: Use the `cosmos_select` tool to check the customer's claim history and policy data. Ensure this is not a duplicate claim based on the `claim_id`.

    3.  **Policy Limit Verification**: Check the claim amount. Ensure it does not exceed the policy's specified limit.

    4.  **Medical Diagnosis Validation**: Use the `get_disease_info` tool to verify that the diagnosis on the doctor's form is a valid diagnosis. If it's not valid, provide a "Rejected" recommendation and state the reason. If it is valid, continue.

    5.  **Treatment Cost Verification**: Check the treatment price on the invoice. Ensure the price is reasonable and corresponds to the given diagnosis. If it's not reasonable, provide a "Rejected" recommendation and state the reason. If it is reasonable, continue.

    6.  **Final Recommendation**: Provide the final recommendation for the `AI_suggestion` column: "Approved", "Rejected", or "Pending".

    7.  **Recommendation Reasoning**: Provide a clear and concise reason for your recommendation. This is for the `AI_reasoning` column. Include specific validation issues found (e.g., name mismatch between invoice and customer data, missing required fields).

    8.  **Update Existing Claim**: Use the `update_claim_with_ai_decision` tool to update the existing claim record with your AI_suggestion, AI_reasoning, and summary. DO NOT create new records.

    IMPORTANT RULES:
    * Answer in **Indonesian** with a concise and professional tone.
    * When using the `cosmos_select` tool, you **must** first use the `get_db_details` tool to get the correct container and column names.
    * If any data is **missing or incomplete**, provide a "Pending" recommendation and explicitly state what specific data is needed.
    * ALWAYS update the existing claim record, never create duplicates.
    * Include detailed reasoning for invalid claims, such as name mismatches, missing fields, etc.

"""

llm = AzureChatOpenAI(
    azure_deployment="gpt-4.1",
    temperature=0.8,
)
tools = [cosmos_select_tool, get_db_details, search_tool, get_disease_info, update_claim_with_ai_decision]

# Initialize agent
Agent = initialize_agent(
    tools,   
    llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    prefix=system_prompt
)

def cosmos_select_raw(query: str, container: str):
    """Raw Cosmos DB query without LangChain tool wrapper"""
    try:
        container_client = database.get_container_client(container)
        items = list(container_client.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        return items
    except Exception as e:
        print(f"Error querying Cosmos DB: {e}")
        return []

def doc_intel(customer_id, claim_id):
    customer_data = cosmos_select_raw(f"SELECT * FROM c WHERE c.customer_id = '{customer_id}'", "customer")
    claim_data = cosmos_select_raw(f"SELECT * FROM c WHERE c.claim_id = '{claim_id}'", "claim")
    document_data = cosmos_select_raw(f"SELECT * FROM c WHERE c.claim_id = '{claim_id}'", "document")
    
    # Find documents by type
    document_invoice = [doc for doc in document_data if doc.get('doc_type') == 'invoice claim']
    docform = [doc for doc in document_data if doc.get('doc_type') == 'doctor form']
    
    # Extract documents from blob storage
    extracted_invoice = {}
    if document_invoice:
        blob_url = document_invoice[0].get('blob_url')
        if blob_url:
            extracted_invoice = extract_invoice(blob_url)
    
    extracted_docform = {}
    if docform:
        blob_url = docform[0].get('blob_url')
        if blob_url:
            extracted_docform = extract_doctor_form(blob_url)
    
    policy_data = []
    if customer_data:
        policy_data = cosmos_select_raw(f"SELECT * FROM c WHERE c.policy_id = '{customer_data[0]['policy_id']}'", "policy")
    
    return {
        "customer_data": customer_data[0] if customer_data else {},
        "claim_data": claim_data[0] if claim_data else {},
        "document_invoice": extracted_invoice,
        "doctor_form_extraction": extracted_docform,
        "policy_data": policy_data[0] if policy_data else {}
    }

analyst_chain = prompt_analyst | llm | parser_claim_analyst | Agent

def analyst_chain_pro(customer_id, claim_id):
    # Get all data from Cosmos DB and extract documents from blob storage
    doc_data = doc_intel(customer_id, claim_id)
    
    import time
    max_retries = 3
    for attempt in range(max_retries):
        try:
            result = analyst_chain.invoke(input={
                "customer_data": doc_data["customer_data"],
                "doctor_form_extraction": doc_data["doctor_form_extraction"],
                "invoice_claim": doc_data["document_invoice"],
                "claim_data": doc_data["claim_data"]
            })
            print(result)
            return result
        except Exception as e:
            if "503" in str(e) or "InternalServerError" in str(e):
                print(f"Azure OpenAI service error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)  # Wait 5 seconds before retry
                    continue
            raise e

dummy_claim1 = {
    "claim": {
        "claim_id": "C007",
        "customer_id": "CU1002",
        "claim_type": "Medical",
        "claim_amount": 7720000,
        "claim_date": "2025-08-01",
        "claim_status": "Prosses",
        "documents": ["D010", "D011"]
    },
    "customer": {
        "customer_id": "CU1002",
        "policy_id": "P002",
        "customer_no": "082145153149",
        "name": "Feri Hussen",
        "dob": "15/03/1985",
        "age": 39,
        "gender": "MALE",
        "NIK": "54321",
        "email": "salsabilaazzhr@gmail.com",
        "is_policy_holder": "True",
        "relation_with_policy_holder": "Self",
        "employment_status": "employ",
        "marital_status": "Married",
        "income": 350000,
        "claim_history": []
    }
}

def upload_form_docs_and_create_claim():
    """Upload documents from /form folder and create claim records"""
    
    # Upload to blob storage
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    print(f"Connection string: {conn_str}")
    if not conn_str:
        print("Error: AZURE_STORAGE_CONNECTION_STRING not found")
        return None
    
    blob_service = BlobServiceClient.from_connection_string(conn_str)
    container_name = "intelegent-document-processing-st"
    
    # File mappings
    files = [
        {"local": "form/dokter_form_siloam.pdf", "blob": "input_folder/doctor_form/dokter_form_siloam.pdf", "type": "doctor form"},
        {"local": "form/invoice_siloam.pdf", "blob": "input_folder/invoice/invoice_siloam.pdf", "type": "invoice claim"}
    ]
    
    uploaded_docs = []
    for file_info in files:
        if os.path.exists(file_info["local"]):
            blob_client = blob_service.get_blob_client(container=container_name, blob=file_info["blob"])
            
            with open(file_info["local"], "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            
            blob_url = f"https://internbatch1a29d.blob.core.windows.net/{container_name}/{file_info['blob']}"
            uploaded_docs.append({
                "blob_url": blob_url,
                "doc_type": file_info["type"]
            })
            print(f"Uploaded: {file_info['local']} -> {blob_url}")
    
    # Create claim using dummy_claim1 data
    claim_id = dummy_claim1["claim"]["claim_id"]
    claim_data = {
        "id": claim_id,
        "claim_id": claim_id,
        "customer_id": dummy_claim1["claim"]["customer_id"],
        "admin_id": "",
        "claim_type": dummy_claim1["claim"]["claim_type"],
        "claim_amount": dummy_claim1["claim"]["claim_amount"],
        "claim_date": dummy_claim1["claim"]["claim_date"],
        "documents": [],
        "summary": "",
        "AI_suggestion": "",
        "AI_reasoning": "",
        "claim_status": dummy_claim1["claim"]["claim_status"]
    }
    
    # Create document records
    doc_ids = []
    for doc in uploaded_docs:
        doc_id = f"D{random.randint(100, 999)}"
        doc_record = {
            "id": doc_id,
            "doc_id": doc_id,
            "claim_id": claim_id,
            "doc_type": doc["doc_type"],
            "blob_url": doc["blob_url"],
            "document_content": {}
        }
        
        # Insert document
        doc_container = database.get_container_client("document")
        doc_container.upsert_item(doc_record)
        doc_ids.append(doc_id)
        print(f"Created document record: {doc_id} ({doc['doc_type']})")
    
    # Update claim with document IDs
    claim_data["documents"] = doc_ids
    
    # Insert claim
    claim_container = database.get_container_client("claim")
    claim_container.upsert_item(claim_data)
    print(f"Created claim: {claim_id}")
    
    return claim_id

def main():
    claim_id = upload_form_docs_and_create_claim()
    result = analyst_chain_pro(customer_id=dummy_claim1["claim"]["customer_id"], claim_id=claim_id)

if __name__ == "__main__":
    main()