import os
import json
import requests
from dotenv import load_dotenv
from azure.cosmos import CosmosClient
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool, Tool
from langchain_community.utilities import SerpAPIWrapper
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from langchain.agents import initialize_agent, AgentType
load_dotenv()
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
        "document_content" : the actual content of the document (contain of extracted document from pedf)
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
        "claim_status" : claim status that were given by the insurance claim officer (the only option are "Approved", "Rejected", "Pending", "Prosses")
        "claim_reason" :  claim status reason why were accepted/rejected by insurance claim officer
        "summary" : the summary of the claim 
        "AI_suggestion" : the suggestion by system for the claim 
        "AI_reasoning" : the reasoning behind the system's suggestion

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

# tool for  rag : 

# tool to do web search
system_prompt = """
    you are an insurance officer's assistant. you will help insurance officer with their tasks. 
    you will also be able to search on cosmos db in documentdb and search for relevant documents.
    RULES 
    1. ANSWER IN THE INDONESIAN LANGUAGE
    2. if you want to use cosmos_select_tool, you MUST to access get_db_details tool before.
    3. WHEN GET THE DB DETAILS, YOU MUST STAY CONSISTANT WITH THE NAME OF CONTAINER AND THE COLUMNS NAME.
    4. ANSWER IN A CLEAR AND CONCISE MANNER, AND DO NOT USE THIRD-PERSON PERSPECTIVE.
    5. if user ask about something that you don't know and don't have the information in database, you may start with using web search tools
"""
llm = AzureChatOpenAI(
    azure_deployment="gpt-4.1",
    temperature=0.8,
)

tools = [cosmos_select_tool, get_db_details, search_tool, get_dieses_info]

# Initialize agent
Agent_Insurance = initialize_agent(
    tools,   
    llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    prefix=system_prompt 
)
print("Agent siap digunakan")
agent_response = Agent_Insurance.run("Coba Cari claim yang telah di approve di database, dapatkan diagnoasanya dan pastikan diagnosa tersebut sesuai valid, lalu pastikan harga pengobatan yang di claim sesuai dengan diagnosa tersebut, lalu buatkan ringkasan singkat untuk claim tersebut dalam bahasa indonesia")
print(agent_response)
