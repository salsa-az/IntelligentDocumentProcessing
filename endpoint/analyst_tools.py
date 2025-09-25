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

@tool("cosmos_select")
def cosmos_select_tool(query: str, container: str, parameters: list = None) -> List[Dict[str, Any]]:
    """Run a Cosmos DB select query. please remember that this is comos db not sql also call the get_DB_details before call this tools"""
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
    1. container name =  "document" 
     container where all the document's detail is stored
    PK: "doc_id" : unique identifier for each document
    FK: "claim_id"
    Attributes:
        "doc_type" : determine the type of document ( invoice, Doctor form)
        "document_content" : the actual content of the document (contain of extracted document from pdf)
    2. container name = "claim" not "claims"
    where all the claim data is store 
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

    3. container name =  "customer"
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

    4. container name =  "policy"
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

    5. container name = "Insurance Administrator"
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
    STAY CONSISTENT WITH ALL NAME FROM COLUMN TO CONTAINER NAME
    """
    return details

search = SerpAPIWrapper()
search_tool = Tool(
    name="web_search",
    description="Search the web for information, use to search the cost treatment to validate the treatment cost",
    func=search.run,
)

# Tool for ICD API 
@tool("get_disease_info")
def get_disease_info(search_key) :
    """search for dieses information from WHO ICD API, to verify the diagnosa, please input in english"""
    url = "https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"
    params = {
        "sf": "code,name",
        "terms": search_key
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        # data[3] biasanya berisi hasil list kode & deskripsi
        results = [{"Code": code, "Description": desc} for code, desc in data[3]]
        return results
    else:
        return {"error": response.status_code, "message": response.text}

@tool('update_claim_and_document')
def update_claim_and_document(claim_id: str, ai_suggestion_status: str, ai_reasoning: str, summary: str) -> str:
    """Update existing claim with AI suggestion status(only Approved/Rejected/Pending), AI Reasoning (reasoning for ai suggestion status), and Summary """
    try : 
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
        
        print(f'Successfully updated claim {claim_id} with AI decision')
        return "done"
    except Exception as e:
        return f"Error updating claim: {e}"
@tool("document_reuierement_info")
def document_reuierement_info():
    """retrive information about document recuirement that claim must have"""
    return document_requirement

