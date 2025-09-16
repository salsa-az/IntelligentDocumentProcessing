import os 
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from azure.cosmos import CosmosClient
from langchain.output_parsers import PydanticOutputParser
from langchain.agents import initialize_agent, AgentType
from prompt import system_prompt_task_addministrative, system_prompt_task_diagnosis_validation, system_prompt_task_treatment_cost_validation, system_prompt_task_decion_making
from analyst_tools import cosmos_retrive_data, get_db_details, get_disease_info, update_claim_and_document, document_reuierement_info, search_tool
from doc_intel import analize_doc
from dotenv import load_dotenv
load_dotenv()

class QueryInput(BaseModel):
    query: str = Field(..., description="Cosmos SQL query, example: SELECT TOP 5 c.id, c.name FROM c")
    container : str = Field(..., description="name container in Cosmos DB")
    parameters: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Opsional. List [{'name':'@param','value':..}] untuk query"
    )

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
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        prefix=System_prompt
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
    doc_invoice = cosmos_retrive_data(f"SELECT * FROM c WHERE c.doc_id=@idParam", "document",parameters=[{
        "name" : "@idParam",
        "value" : claim_data['documents'][0]
    }] )
    doc_invoice = doc_invoice[0]
    doc_docform = cosmos_retrive_data(f"SELECT * FROM c WHERE c.doc_id=@idParam", "document",parameters=[{
        "name" : "@idParam",
        "value" : claim_data['documents'][1]
    }])
    doc_docform = doc_docform[0]
    invoice_content = analize_doc(doc_invoice["doc_blob_address"], "prebuilt-invoice")
    docform_content = analize_doc(doc_docform["doc_blob_address"], "form_doctor")
    doc_invoice["doc_contents"] = invoice_content
    doc_docform["doc_contents"] = docform_content
    input_agent = {
        "customer_data" : customer_data, 
        "doctor_form_extraction" : doc_docform, 
        "invoice_claim" : doc_invoice,
        "claim_data" : claim_data
    }
    agent_administrative = creating_agent([document_reuierement_info], system_prompt_task_addministrative)
    print("initialize agent_administrative")
    result_administrative = agent_administrative.invoke(input={"input" : input_agent})
    agent_diag_val = creating_agent([get_disease_info], system_prompt_task_diagnosis_validation)
    print("initialize agent_med_val")
    agent_treat_cost_val = creating_agent([search_tool], system_prompt_task_treatment_cost_validation)
    result_treat_cost = agent_treat_cost_val.invoke(input={"input" : input_agent})
    result_treat_cost = result_treat_cost['output']
    result_diag_val = agent_diag_val.invoke(input={"input" : input_agent})
    result_administrative = result_administrative['output']
    result_diag_val = result_diag_val['output']
    input_agent['result_administrative_validation'] = result_administrative
    input_agent['result_treatment_cost_validation'] = result_treat_cost
    input_agent['result_diagnosis_validation'] = result_diag_val
    agent_final_decision = creating_agent([update_claim_and_document], system_prompt_task_decion_making)
    agent_final_decision.invoke(input={"input" : input_agent})
