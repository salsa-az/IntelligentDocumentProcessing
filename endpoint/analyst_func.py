import os 
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from azure.cosmos import CosmosClient
from langchain.output_parsers import PydanticOutputParser
from langchain.agents import initialize_agent, AgentType
from langchain.schema import SystemMessage
from prompt import system_prompt_task_addministrative, system_prompt_task_diagnosis_validation, system_prompt_task_treatment_cost_validation, system_prompt_task_decion_making, system_prompt_task_history_checking
from analyst_tools import cosmos_retrive_data, get_db_details, get_disease_info , update_claim_and_document, document_reuierement_info, search_tool, cosmos_select_tool
from doc_intel import analize_doc
from dotenv import load_dotenv
load_dotenv()
cosmos_db_uri = os.getenv("COSMOS_DB_URI")
cosmos_db_key = os.getenv("COSMOS_DB_KEY")
database_name = os.getenv("COSMOS_DB_DATABASE_NAME")

client = CosmosClient(cosmos_db_uri, credential=cosmos_db_key)
database = client.get_database_client("dokumenI-intelejen-db")
# Initialize LLM 
llm = AzureChatOpenAI(
    azure_deployment="gpt-4.1",
    temperature=0.8,
)
# Define tools for the Fact checking agent
#tools = [get_db_details, cosmos_select, get_disease_info, update_claim_and_document, document_reuierement_info]

# Initialize Fact checking agent
def creating_agent(tools, System_prompt) :
    Agent = initialize_agent(
        tools,   
        llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True,
        agent_kwargs={"sytem_message": SystemMessage(content=System_prompt)}
    )
    return Agent

def analyst_function_executor(cus_id, claim_id) : 
    print(cus_id)
    customer_data = cosmos_retrive_data(f"SELECT * FROM c WHERE c.customer_id= @customeridParam", "customer", parameters=[{
        "name" : "@customeridParam",
        "value" : cus_id
    }] )
    customer_data = customer_data[0]
    claim_data = cosmos_retrive_data(f"SELECT * FROM c WHERE c.claim_id=@idParam", "claim",parameters=[{
        "name" : "@idParam",
        "value" : claim_id
    }] )
    claim_data =  claim_data[0]
    container_client = database.get_container_client("document")
    document_datas = {}
    for id in claim_data['documents'] : 
        doc_data = cosmos_retrive_data(f"SELECT * FROM c WHERE c.doc_id=@idParam", "document",parameters=[{
        "name" : "@idParam",
        "value" : id
        }])
        doc_data = doc_data[0]
        content = analize_doc( doc_data["doc_blob_address"], doc_data["doc_type"])
        doc_data['doc_contents'] = content
        container_client.upsert_item(doc_data)
        document_datas[doc_data["doc_type"]] = doc_data
    agent_administrative = creating_agent([document_reuierement_info], system_prompt_task_addministrative)
    print("initialize agent_administrative")
    result_administrative = agent_administrative.invoke(input={"input" : {"input" : {
        "claim data" : claim_data,
        "documents" : document_datas
    }}})
    agent_diag_val = creating_agent([get_disease_info], system_prompt_task_diagnosis_validation)
    agent_treat_cost_val = creating_agent([search_tool], system_prompt_task_treatment_cost_validation)
    result_treat_cost = agent_treat_cost_val.invoke(input={"input" : {"input" : {
        "claim data" : claim_data,
        "invoice data" : document_datas['invoice']
    }}})
    result_treat_cost = result_treat_cost['output']
    result_diag_val = agent_diag_val.invoke(input={"input" : {"input" : {"input" : {
        "claim data" : claim_data,
        "doctor form" : document_datas["doctor form"]
    }}}})
    agent_history_checking = creating_agent([cosmos_select_tool, get_db_details], system_prompt_task_history_checking)
    result_history_checking = agent_history_checking.invoke(input=f"search the entire claim beheivior of this person{customer_data}")
    result_history_checking = result_history_checking['output']
    result_administrative = result_administrative['output']
    result_diag_val = result_diag_val['output']
    agent_final_decision = creating_agent([update_claim_and_document], system_prompt_task_decion_making)
    agent_final_decision.invoke(input={"input" : {
        "customer data" : customer_data,
        "claim data" : claim_data,
        "documents" : document_datas,
        "result administrative validation" : result_administrative,
        "result Diagnosis Validation": result_diag_val,
        "result Treatment cost validation" : result_treat_cost,
        "result history checking" : result_history_checking
    }})
