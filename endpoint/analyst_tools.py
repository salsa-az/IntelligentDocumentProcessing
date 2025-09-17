import os
import requests
from azure.cosmos import CosmosClient
from langchain.tools import tool, Tool
from typing import List, Dict, Any, Optional
from langchain_community.utilities import SerpAPIWrapper
from dotenv import load_dotenv
from prompt import document_requirement
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()
cosmos_db_uri = os.getenv("COSMOS_DB_URI")
cosmos_db_key = os.getenv("COSMOS_DB_KEY")
database_name = os.getenv("COSMOS_DB_DATABASE_NAME")

client = CosmosClient(cosmos_db_uri, credential=cosmos_db_key)
database = client.get_database_client("dokumenI-intelejen-db")

def cosmos_retrive_data(query: str, container: str, parameters: list = None) -> List[Dict[str, Any]]:
    """Run a Cosmos DB select query."""
    try:
        container_client = database.get_container_client(container)
        items = list(container_client.query_items(
            query=query,
            enable_cross_partition_query=True,
            parameters=parameters
        ))
        print(f"Query executed successfully. Retrieved {len(items)} items.")
        return items
    except Exception as e:
       print(f"Error querying Cosmos DB: {e}")
       return []


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

search = SerpAPIWrapper()
search_tool = Tool(
    name="web_search",
    description="Search the web for information, use to search the cost treatment to validate the treatment cost",
    func=search.run,
)

@tool("get_disease_info")
def get_disease_info(search_key : str):
    """search for disease information from WHO ICD XI API, to verify the diagnosa. given the diagnosis in english not the diagnosis code and tool will return the information. if it return empty dict it means there is no info in there """
    try : 
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
                if score >= 0.8:
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
        if finalData == {} : 
            return "there is no information about the claim"
        return finalData
    except : 
        print("eror")
        return "there is no information"

@tool('update_claim_and_document')
def update_claim_and_document(claim_id: str, ai_suggestion_status: str, ai_reasoning: str, summary: str, invoice_doc_id : str, invoice_doc_contents : dict, doctor_form_doc_id : str, doctor_form_doc_contents : dict) -> str:
    """Update existing claim with AI suggestion status(only Approved/Rejected/Pending), AI Reasoning (reasoning for ai suggestion status), Summary and invoice document data's doc_id and doc_contents, also doctor Form document data's doc_id and doc_contents"""
    try:
        container_client = database.get_container_client("claim")
        claim_data = cosmos_retrive_data(f"SELECT * FROM c WHERE c.claim_id= @idParam", "claim", parameters=[{
            "name" : "@idParam",
            "value" : claim_id
        }] )
        claim_data =  claim_data[0]
        claim_data['AI_suggestion'] = ai_suggestion_status
        claim_data['AI_reasoning'] = ai_reasoning        
        claim_data['summary'] = summary
        container_client.upsert_item(claim_data)
        container_client = database.get_container_client("document")
        doc_ids = [invoice_doc_id, doctor_form_doc_id] 
        doc_contents = [invoice_doc_contents, doctor_form_doc_contents]
        for i in range(2):
            doc_data = cosmos_retrive_data(f"SELECT * FROM c WHERE c.doc_id=@idParam", "document",parameters=[{
                "name" : "@idParam",
                "value" : doc_ids[i]
            }])
            doc_data = doc_data[0]
            doc_data['doc_content'] = doc_contents[i]
            container_client.upsert_item(doc_data)
        print(f'Successfully updated claim {claim_id} with AI decision')
        return "done"
    except Exception as e:
        return f"Error updating claim: {e}"
@tool("document_reuierement_info")
def document_reuierement_info():
    """retrive information about document recuirement that claim must have"""
    return document_requirement

