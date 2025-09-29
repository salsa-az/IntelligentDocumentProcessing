import os 
import requests
from dotenv import load_dotenv
from typing import List, Dict, Any
from azure.cosmos import CosmosClient

load_dotenv()
cosmos_db_uri = os.getenv("COSMOS_DB_URI")
cosmos_db_key = os.getenv("COSMOS_DB_KEY")
database_name = os.getenv("COSMOS_DB_DATABASE_NAME")
client = CosmosClient(cosmos_db_uri, credential=cosmos_db_key)
database = client.get_database_client("dokumenI-intelejen-db")
analyst_triger_url = os.getenv("analyst_function_url")
notify_triger_url = os.getenv("notify_function_url")
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
def url_triger(url, params) : 
    """Trigger a function via HTTP POST request."""
    try : 
        response = requests.post(url, json=params)
        if response.status_code == 200 :
            return response.json()
        else : 
            print(f"Error triggering function: {response.status_code} - {response.text}")
            return None
    except Exception as e : 
        print(f"Exception during function trigger: {e}")
        return None

def function_triger(customer_id, claim_id, approver = None):
    """Trigger the analyst function for a specific customer and claim."""
    try:
        if approver == None : 
            params = {
                "customer_id": customer_id,
                "claim_id": claim_id
            }
            return url_triger(analyst_triger_url, params)
        else : 
            params = {
                "customer_id": customer_id,
                "claim_id": claim_id,
                "approver": approver
            }
            return url_triger(notify_triger_url, params)
    except Exception as e:
        print(f"Error triggering analyst function: {e}")
        return None