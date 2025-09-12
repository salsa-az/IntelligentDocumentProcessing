import os 
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from azure.cosmos import CosmosClient
from langchain.output_parsers import PydanticOutputParser
from langchain.agents import initialize_agent, AgentType
from prompt_analyst_func import document_requirement, Sys_promt_claim_analysis, system_prompt_agent
from funcHelp_analyst import cosmos_retrive_data
from document_intelegent import analize_doc
from anlisystToolAgent import cosmos_select_tool, get_db_details, search_tool, get_disease_info, update_claim_with_ai_decision
from dotenv import load_dotenv
from langchain_core.runnables import RunnableParallel, RunnableLambda
load_dotenv()

cosmos_db_uri = os.getenv("COSMOS_DB_URI")
cosmos_db_key = os.getenv("COSMOS_DB_KEY")
database_name = os.getenv("COSMOS_DB_DATABASE_NAME")

client = CosmosClient(cosmos_db_uri, credential=cosmos_db_key)
database = client.get_database_client(database_name)

class ClaimEvaluation(BaseModel):
    claim_id: str = Field(..., description="Unique identifier for the claim")
    completeandsyncronisestatus: bool = Field(..., description="is the document allready complete and syncronise. DO NOT GIVE ANY OTHER STATUS AND EXPLANATION")
    Claim_summary: str = Field(description="Summary of the claim")
    input_customer_data: dict = Field(description="data mentah customer data diinputkan")
    input_claim_data: dict = Field(description="data mentah claim detail yang diinputkan")
    input_document_invoice_data: dict = Field(description="data mentah invoice yang diinputkan")
    input_document_doctorform_data: dict = Field(description="data mentah doctor data yang diinputkan")

class QueryInput(BaseModel):
    query: str = Field(..., description="Cosmos SQL query, example: SELECT TOP 5 c.id, c.name FROM c")
    container : str = Field(..., description="name container in Cosmos DB")
    parameters: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Opsional. List [{'name':'@param','value':..}] untuk query"
    )

# Prompt Configuration
parser_claim_analyst = PydanticOutputParser(pydantic_object=ClaimEvaluation)
prompt_analyst = PromptTemplate(
        input_variables=["customer_data", "doctor_form_extraction", "invoice_claim", "claim_data"],
        template=Sys_promt_claim_analysis,
        partial_variables={"format_output": parser_claim_analyst.get_format_instructions(), "document_requirement": document_requirement},
        )

# Initialize LLM 
llm = AzureChatOpenAI(
    azure_deployment="gpt-5-chat",
    temperature=0.4,
)
# Define tools for the Fact checking agent
tools = [cosmos_select_tool, get_db_details, search_tool, get_disease_info, update_claim_with_ai_decision]

# Initialize Fact checking agent
agent = initialize_agent(
    tools,   
    llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    prefix=system_prompt_agent
)
# Main chain for claim analysis and decision sugestion

def document_intelegent(ids) :
    cus_id = ids["cus_id"]
    claim_id = ids['claim_id'] 
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
    input_agent ={ "input" :{"customer_data" : customer_data, 
        "doctor_form_extraction" : doc_docform, 
        "invoice_claim" : doc_invoice,
        "claim_data" : claim_data}}
    return input_agent
doc_intel = RunnableLambda(document_intelegent)
analyst_chain = document_intelegent | agent 
    
