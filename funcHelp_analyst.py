import os
from typing import List, Dict, Any, Optional
from azure.cosmos import CosmosClient
cosmos_db_uri = os.getenv("COSMOS_DB_URI")
cosmos_db_key = os.getenv("COSMOS_DB_KEY")
database_name = os.getenv("COSMOS_DB_DATABASE_NAME")

client = CosmosClient(" ", credential=" ")
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