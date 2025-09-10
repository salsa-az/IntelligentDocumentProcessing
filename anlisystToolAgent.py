import os
import requests
from azure.cosmos import CosmosClient
from langchain.tools import tool, Tool
from typing import List, Dict, Any, Optional
from langchain_community.utilities import SerpAPIWrapper
cosmos_db_uri = os.getenv("COSMOS_DB_URI")
cosmos_db_key = os.getenv("COSMOS_DB_KEY")
database_name = os.getenv("COSMOS_DB_DATABASE_NAME")

client = CosmosClient(cosmos_db_uri, credential=cosmos_db_key)
database = client.get_database_client(database_name)


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