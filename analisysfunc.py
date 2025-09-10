from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.agents import initialize_agent, AgentType
from prompt_analyst_func import document_requirement, Sys_promt_claim_analysis, system_prompt
from anlisystToolAgent import cosmos_select_tool, get_db_details, search_tool, get_disease_info, update_claim_with_ai_decision
from dotenv import load_dotenv
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
parser_claim_decision = PydanticOutputParser(pydantic_object=ClaimSuggestion)

# Initialize LLM 
llm = AzureChatOpenAI(
    azure_deployment="gpt-4.1",
    temperature=0.8,
)
# Define tools for the Fact checking agent
tools = [cosmos_select_tool, get_db_details, search_tool, get_disease_info, update_claim_with_ai_decision]

# Initialize Fact checking agent
Agent = initialize_agent(
    tools,   
    llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    prefix=system_prompt
)

# Main chain for claim analysis and decision sugestion
analyst_chain = prompt_analyst | llm | parser_claim_analyst | Agent



