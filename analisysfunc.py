from langchain.tools import tool, Tool
import os
from pydantic import BaseModel, Field
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.agents import initialize_agent, AgentType
from dotenv import load_dotenv
import json
from pyparsing import Dict
from langchain_community.utilities import SerpAPIWrapper
from langchain.agents import initialize_agent, AgentType
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
from typing import List, Dict, Any, Optional
import re
import requests 
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


"""class ClaimEvaluation(BaseModel):
    claim_id: str = Field(..., description="Unique identifier for the claim")
    decision: str = Field(..., description="the final Suggestion, the only option is Approved/Rejected/Pending. DO NOT GIVE ANY OTHER STATUS AND EXPLANATION")
    reason: str = Field(..., description="Explanation for the decision")
    summary: str = Field(description="Summary of the claim")
    input_customer_data: dict = Field(description="data mentah customer data diinputkan")
    input_claim_data: dict = Field(description="data mentah claim detail yang diinputkan")
    input_document_invoice_data: dict = Field(description="data mentah invoice yang diinputkan")
    input_document_doctorform_data: dict = Field(description="data mentah doctor data yang diinputkan")"""
cosmos_db_uri = os.getenv("COSMOS_DB_URI")
cosmos_db_key = os.getenv("COSMOS_DB_KEY")
database_name = os.getenv("COSMOS_DB_DATABASE_NAME")

# --- Client sederhana ---
client = CosmosClient(cosmos_db_uri, credential=cosmos_db_key)
database = client.get_database_client(database_name)

# tool to search in cosmos db
# --- Schema input untuk tool ---
class QueryInput(BaseModel):
    query: str = Field(..., description="Cosmos SQL query, example: SELECT TOP 5 c.id, c.name FROM c")
    container : str = Field(..., description="name container in Cosmos DB")
    parameters: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Opsional. List [{'name':'@param','value':..}] untuk query"
    )

# --- Tool SELECT ---
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

# tool for web search 
search = SerpAPIWrapper()
search_tool = Tool(
    name="web search",
    description="Search the web for information, useful for when you need to find current information or look up specific details online.(e.g. berapa harga rata-rata pengobatan untuk penyakit X di Indonesia?)",
    func=search.run,
)

# Tool for ICD API 
@tool("get_dieses_info")
def get_dieses_info(search_key, min_score=0.5) :
    """search for dieses information from WHO ICD API, to verify the diagnosa"""

    token_endpoint = 'https://icdaccessmanagement.who.int/connect/token'
    client_id = 'ef108bbc-154c-401a-b7ba-15758a60c878_1bd261be-3e0f-495a-ae9d-1f8c0967ed04'
    client_secret = '2gmDnJPBN5CxYl8HxOgS720MtPTWyIb3M0az0Kf/bUI='
    scope = 'icdapi_access'
    grant_type = 'client_credentials'
    # set data to post
    payload = {'client_id': client_id, 
            'client_secret': client_secret, 
            'scope': scope, 
            'grant_type': grant_type}
            
    # make request
    r = requests.post(token_endpoint, data=payload, verify=False).json()
    token = r['access_token']

    # access ICD API


    # HTTP header fields to set
    headers = {'Authorization':  'Bearer '+token, 
            'Accept': 'application/json', 
            'Accept-Language': 'en',
        'API-Version': 'v2'}
    uri = f'https://id.who.int/icd/entity/search?q={search_key}'

    # make request
    searchData = requests.get(uri, headers=headers, verify=False)
    searchData = searchData.json()
    finalData = {}
    # Memastikan respons berisi daftar entitas yang diharapkan
    if "destinationEntities" in searchData and isinstance(searchData["destinationEntities"], list):

        for i, entity in enumerate(searchData["destinationEntities"]):
            score = entity.get("score", 0)
            print(entity)
            if score >= min_score:
                # Mendapatkan data utama dari setiap entitas
                title = entity.get("title", "Tidak tersedia").replace("<em>", "").replace("</em>", "")
                entity_id = entity.get("id", "Tidak tersedia")
                score = entity.get("score", "Tidak tersedia")
                response = requests.get(entity_id, headers=headers, verify=False)
                response.raise_for_status()
                response = response.json()
                detail = response.get('definition') 
                if detail:
                    # Menghapus tag HTML dari definisi
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

@tool('add_cosmosDB')
def add_cosmosDB(item_claim : dict, item_doc : dict, item_invoice : dict) -> str : 
    """claim item, doc item and invoice item is in dict format"""
    try:
        cosmos_db_uri = os.getenv("COSMOS_DB_URI")
        cosmos_db_key = os.getenv("COSMOS_DB_KEY")
        database_name = os.getenv("COSMOS_DB_DATABASE_NAME")
        # Inisialisasi CosmosClient
        client = CosmosClient(cosmos_db_uri, credential=cosmos_db_key)
        # Mendapatkan referensi ke database
        # menambahkan id 
        item_claim['id'] = str(random.randint(100000, 999999))
        item_claim['claim_status'] = "Prosses"
        item_doc['id'] = str(random.randint(100000, 999999))
        item_invoice['id'] = str(random.randint(100000, 999999))
        database = client.get_database_client(database_name)
        container_names = ["claim", "document", "document"]
        items = [item_claim, item_doc, item_invoice]
        for i in range(len(container_names)):
            container = database.get_container_client(container_names[i])
            created_document = container.upsert_item(body=  items[i])
        print(f'successfully created document: {created_document}')
        return "done"
    except Exception as e:
        return f"Terjadi kesalahan saat menambahkan dokumen ke Cosmos DB: {e}"

parser_claim_analyst = PydanticOutputParser(pydantic_object=ClaimEvaluation)
document_requirement = """
    Here is the requirement of each document

    Doctor form document requirement :
        Note: The requirements listed below may or may not be written in the same order as they appear in the document. Please ensure all required information is present, regardless of order.
        Doctor form document requirement :
        1. Patient Administrative Data
            - Admission Date - Format: DD/MM/YYYY
            - Discharge Date - Format: DD/MM/YYYY

        2. Doctor-Patient Relationship
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
        5. Description of Services/Procedures Provided
        6. Itemized List of Charges (each service/procedure with cost)
        7. Total Amount Due
        8. Currency
        9. Hospital/Provider Name
        11. Hospital/Provider Address
        12. Hospital/Provider Contact Information (phone/email)
        13. Attending Doctor's Name (if applicable)
        14. Payment Instructions or Method
        15. Notes/Remarks (if any)
        16. Official Stamp/Seal of Hospital (if required)
        17. Signature of Authorized Hospital Staff (if required)

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

# tool for  rag : 

parser_claim_decision = PydanticOutputParser(pydantic_object=ClaimSuggestion)
# tool to do web search
system_prompt = F"""
    You are an insurance claims assistant. Your purpose is to provide a claim recommendation—whether it should be **Approved**, **Rejected**, or **Pending**—based on the data provided.

    YOU MUST FOLLOW THIS PROCESS BEFORE GIVING THE RECOMMENDATION:

    1.  **Initial Validation**: Check the validation status from the input. If the status is "NOT VALID", proceed directly to **Step 6**. If the status is "VALID", continue to the next step.

    2.  **Duplicate Claim Check**: Use the `cosmos_select` or 'add_cosmosDB' tool to check the customer's claim history and policy data. Ensure this is not a duplicate claim based on the `claim_id` or similar `diagnosa` and `tanggal_klaim`.

    3.  **Policy Limit Verification**: Check the claim amount. Ensure it does not exceed the policy's specified limit.

    4.  **Medical Diagnosis Validation**: Use the `get_dieses_info` tool to verify that the diagnosis on the doctor's form is a valid diagnosis. If it's not valid, provide a "Rejected" recommendation and state the reason. If it is valid, continue.

    5.  **Treatment Cost Verification**: Check the treatment price on the invoice. Ensure the price is reasonable and corresponds to the given diagnosis. If it's not reasonable, provide a "Rejected" recommendation and state the reason. If it is reasonable, continue.

    6.  **Final Recommendation**: Provide the final recommendation for the `AI_suggestion` column: "Approved", "Rejected", or "Pending".

    7.  **Recommendation Reasoning**: Provide a clear and concise reason for your recommendation. This is for the `AI_reasoning` column.

    8.  **Data Insertion to Cosmos DB**: this will be to insert  claim item into "claim" container &  extracted document(invoice & doctor form) item into "document" container and the item format is this : 
        claim item : 
        "claim_id" : <claim_id from the input>
        "customer_id" : <customer_id from the input>
        "admin_id" : ""
        "claim_type" : <claim_type from the input>
        "claim_amount" : <claim_amount from the input>
        "claim_date" : <claim_date from the input>
        "documents" : <list of document_id related to the claim>
        "claim_status" : ""<leave this empty>
        "claim_reason" :  "" <leave this empty>
        "summary" : <pass from the input>
        "AI_suggestion" : <the suggestion by system for the claim by AI Agent>
        "AI_reasoning" : <the reasoning behind the system's suggestion by AI Agent>
        --------------------------------------------------------------------------
        document item (for each document, invoice & doctor form) :
        "doc_id" : <unique identifier for each document, from the input>
        "claim_id" : <claim_id from the input>
        "doc_type" : <document_type from the input>
         "document_content" : <document_content from the input>
    IMPORTANT RULES:

    * Answer in **English** with a concise and professional tone.
    * When using the `cosmos_select` tool, you **must** first use the `get_db_details` tool to get the correct container and column names. **Maintain consistency with these names.**
    * If any data is **missing or incomplete**, provide a "Pending" recommendation and explicitly state what specific data is needed.
    * You will only insert invoice and doctor's form data into the documents container.

"""
#llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.6)

llm = AzureChatOpenAI(
    azure_deployment="gpt-4.1"
)

tools = [cosmos_select_tool, get_db_details, search_tool, get_dieses_info, add_cosmosDB]
 

# Initialize agent
Agent = initialize_agent(
    tools,   
    llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    prefix=system_prompt
)


analyst_chain = prompt_analyst | llm | parser_claim_analyst | Agent 

def analyst_chain_pro(customer_data, doctor_form_extraction, invoice_claim, claim_data):
    result = analyst_chain.invoke({
        "customer_data": customer_data,
        "doctor_form_extraction": doctor_form_extraction,
        "invoice_claim": invoice_claim,
        "claim_data": claim_data
    })
    print(result['output'])
dummy_claim1 = {
    "claim": {
        "claim_id": "C005",
        "customer_id": "CU1001",
        "claim_type": "Medical",
        "claim_amount": 1200000,
        "claim_date": "2025-08-01",
        "claim_status": "Prosses",
        "documents": ["D006", "D007"]
    },
    "document_form": {
        "document_name": "Medical Report - RS Harapan Bunda",
        "doc_id" : "D007",
        "document_type": "doctor Form",
        "claim_id": "C001",
        "document_content": {
            "hospital": "RS Harapan Bunda",
            "doctor": "Dr. Siti Rahma",
            "diagnosis": "Demam Berdarah",
            "treatment": "Rawat Inap 5 hari",
            "date_issued": "2025-07-30"
        }
    },
    "customer": {
        "customer_id": "CU1001",
        "policy_id": "P001",
        "customer_no": "CUST-2025-01",
        "name": "Budi Santoso",
        "dob": "1990-04-12",
        "age": 35,
        "gender": "Male",
        "NIK": "3174051204900001",
        "email": "salsabilaazzhr@gmail.com",
        "is_policy_holder": True,
        "realtion_with_policy_holder": "Self",
        "employment_status": "Full-time",
        "marrital_status": "Married",
        "income": 12000000,
        "claim_history": ["C001"]
    }, 
    "invoice": {
        "doc_id" : "D006",
        "document_name": "Invoice - RS Harapan Bunda",
        "document_type": "invoice claim",
        "claim_id": "C001",
        "document_content": {
            "invoice_no": "INV-2025-0001",
            "date": "2025-07-30",
            "amount": 1200000,
            "items": [
                {"description": "Rawat Inap 5 hari", "cost": 1000000},
                {"description": "Obat-obatan", "cost": 200000}
            ],
            "hospital": "RS Harapan Bunda"
        }
    }
}
analyst_chain_pro(
    customer_data=dummy_claim1["customer"],
    doctor_form_extraction=dummy_claim1["document_form"],
    invoice_claim=dummy_claim1["invoice"],
    claim_data=dummy_claim1["claim"])

