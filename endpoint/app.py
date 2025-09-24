import sys
import os
import requests
import threading
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import uuid
from datetime import datetime

# Flask
from flask import Flask, request, jsonify
from flask_cors import CORS

# Azure
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient
from endpoint.analyst_func import analyst_function_executor

# Langchain Functions
from endpoint.analyst_func import analyst_function_executor
from doc_intel import analize_doc
from analyst_tools import cosmos_retrive_data
from dotenv import load_dotenv
# from letterfunc import letter_chain_pro  # Temporarily commented out due to credential issues
from chatbotClaimerOfficer import Agent_Insurance
from doc_intel_for_registration import analize_doc as analize_doc_registration

load_dotenv()

# Azure setup
blob_connection_string = os.getenv("BLOB_STRING_CONECTION")
if not blob_connection_string:
    raise ValueError("BLOB_STRING_CONECTION environment variable not set")

blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
cosmos_client = CosmosClient(os.getenv("COSMOS_DB_URI"), credential=os.getenv("COSMOS_DB_KEY"))
database = cosmos_client.get_database_client(os.getenv("COSMOS_DB_DATABASE_NAME"))

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

@app.route('/api/analyze-claim', methods=['POST'])
def analyze_claim():
    """Analyze claim using customer_id and claim_id"""
    try:
        data = request.json
        customer_id = data.get('customer_id')
        claim_id = data.get('claim_id')
        
        if not customer_id or not claim_id:
            return jsonify({'error': 'customer_id and claim_id required'}), 400
        
        # Run analysis
        analyst_function_executor(customer_id, claim_id)
        
        return jsonify({'status': 'success', 'message': 'Analysis completed'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/approved-claim', methods=['GET'])
def approved_claim():
    """Approved all the claim that the user need"""
    try:
        claim_id = request.form.get('claim_id')
        admin_id = request.form.get('admin_id')
        claim_data = cosmos_retrive_data("SELECT * FROM c WHERE c.claim_id=@idParam","claim", [{"name": "@idParam", "value": claim_id}])
        claim_data = claim_data[0]
        admin_data = cosmos_retrive_data("SELECT * FROM c WHERE c.admin_id=@idParam","insurance_admin", [{"name": "@idParam", "value": admin_id}])
        admin_data = admin_data[0]
        customer_data = cosmos_retrive_data("SELECT * FROM c WHERE c.admin_id=@idParam","customer", [{"name": "@idParam", "value": claim_data['customer_id']}])
        policy_data = cosmos_retrive_data("SELECT * FROM c WHERE c.admin_id=@idParam","policy", [{"name": "@idParam", "value": claim_data['policy_id']}])
        # letter_chain_pro(customer_data, claim_data, policy_data, admin_data)  # Temporarily commented out
        return jsonify({'status': 'success', 'data': claim_data})
    except Exception as e : 
        return jsonify({'error': str(e)}), 500
    


@app.route('/api/query', methods=['GET'])
def query_from_cosmosDB() : 
    """Query all the data that needed from cosmosDB"""
    try : 
        query = request.form.get('query')
        container = request.form.get('container')
        parameter = request.form.get('parameter')
        return cosmos_retrive_data(query, container, parameter)
    except Exception as e : 
        return jsonify({'error': str(e)}), 500

@app.route('/api/claims', methods=['GET'])
def get_all_claims():
    """Retrieve all claims from CosmosDB"""
    try:
        claims = list(database.get_container_client("claim").query_items(
            query="SELECT * FROM c",
            enable_cross_partition_query=True
        ))
        return claims
    except Exception as e:
        print(f"Error retrieving claims: {e}", file=sys.stderr)
        return []
    
def safe_fetch_documents(claim_documents):
    """Safely fetch documents with proper error handling"""
    documents = []
    if not claim_documents:
        return documents
    
    for doc_id in claim_documents:
        try:
            doc_data = cosmos_retrive_data(
                "SELECT * FROM c WHERE c.doc_id = @docId", 
                "document", 
                [{"name": "@docId", "value": doc_id}]
            )
            if doc_data and len(doc_data) > 0:
                documents.append(doc_data[0])
            else:
                print(f"Document {doc_id} not found in database")
        except Exception as e:
            print(f"Error fetching document {doc_id}: {e}")
            continue
    
    return documents

@app.route('/api/claims/all-detailed', methods=['GET'])
def get_all_claims_detailed():
    """Get all claims with customer details for approvers - Optimized"""
    try:
        # Get all claims with better error handling
        claims = cosmos_retrive_data(
            "SELECT * FROM c ORDER BY c._ts DESC", 
            "claim", 
            []
        )
        
        if not claims:
            return jsonify({
                'status': 'success',
                'claims': []
            })
        
        # Enrich each claim
        for claim in claims:
            # Get customer data safely
            claim['customer_details'] = claim.get('customer_id')
            
            # Get documents safely (THIS IS THE KEY FIX)
            claim['document_details'] = safe_fetch_documents(claim.get('documents', []))
        
        return jsonify({
            'status': 'success',
            'claims': claims
        })
        
    except Exception as e:
        print(f"Error in get_all_claims_detailed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/claims/<claim_id>/update-status', methods=['POST'])
def update_claim_status(claim_id):
    try:
        data = request.json
        status = data.get('status')
        admin_id = data.get('admin_id')
        notes = data.get('notes', '')
        if not status or not admin_id:
            return jsonify({'error': 'status and admin_id required'}), 400

        # Read the existing claim
        claim_data = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.claim_id = @claimId",
            "claim",
            [{"name": "@claimId", "value": claim_id}]
        )
        if not claim_data:
            return jsonify({'error': 'Claim not found'}), 404

        claim = claim_data[0]
        # Update only the status and related fields
        claim['claim_status'] = status
        claim['admin_id'] = admin_id
        claim['admin_notes'] = notes
        claim['processed_date'] = datetime.now().isoformat()
        if status == 'Approved':
            claim['approved_by'] = admin_id
            claim['approved_date'] = datetime.now().isoformat()
        elif status == 'Rejected':
            claim['rejected_by'] = admin_id
            claim['rejected_date'] = datetime.now().isoformat()
            claim['rejection_reason'] = notes

        # Write back the updated claim
        updated_claim = database.get_container_client("claim").upsert_item(claim)
        # letter_chain_pro(claim['customer_id'], claim_id, f"{admin_id}")  # Temporarily commented out
        return jsonify({'status': 'success', 'claim': updated_claim}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/customer/<customer_id>/claims-detailed', methods=['GET'])
def get_customer_claims_detailed(customer_id):
    """Get detailed claims for a specific customer with documents"""
    try:
        # Get claims for customer
        claims = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.customer_id = @customerId ORDER BY c._ts DESC", 
            "claim", 
            [{"name": "@customerId", "value": customer_id}]
        )
        
        # For each claim, get documents
        for claim in claims:
            if claim.get('documents'):
                documents = []
                for doc_id in claim['documents']:
                    try:
                        doc_data = cosmos_retrive_data(
                            "SELECT * FROM c WHERE c.doc_id = @docId", 
                            "document", 
                            [{"name": "@docId", "value": doc_id}]
                        )
                        if doc_data:
                            documents.append(doc_data[0])
                    except Exception as e:
                        print(f"Error fetching document {doc_id}: {e}")
                claim['document_details'] = documents
                print(f"Fetched {len(documents)} documents for claim {claim.get('claim_id')}")
            else:
                claim['document_details'] = []
        
        return jsonify({
            'status': 'success',
            'claims': claims
        })
        
    except Exception as e:
        print(f"Error in get_customer_claims_detailed: {e}")
        return jsonify({'error': str(e)}), 500

def validate_customer_data(form_data, customer_data):
    """Validate form data against database customer record"""
    if not customer_data:
        return False, "Customer not found in database"
    
    customer = customer_data[0]
    
    # Check if form data matches database
    form_customer_id = form_data.get('customerId')
    form_policy_id = form_data.get('policyId')
    
    print(f"Validating customer_id: {form_customer_id} with database customer_id: {customer['customer_id']}")
    print(f"Validating policy_id: {form_policy_id} with database policy_id: {customer['policy_id']}")

    if customer['customer_id'] != form_customer_id:
        return False, "Customer ID mismatch"
    
    if customer['policy_id'] != form_policy_id:
        return False, "Policy ID mismatch"
    
    return True, "Valid customer"

@app.route('/api/submit-claim', methods=['POST'])
def submit_claim():
    """Submit claim form with file uploads"""
    try:
        # Get form data
        claim_type = request.form.get('claimType')
        claim_amount = request.form.get('claimAmount')
        currency = request.form.get('currency')
        customer_id = request.form.get('customerId')
        policy_id = request.form.get('policyId')
        
        # Get customer data from database
        customer_data = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.customer_id = @customerId", 
            "customer", 
            [{"name": "@customerId", "value": customer_id}]
        )
        
        # Validate customer exists and data matches
        is_valid, message = validate_customer_data(request.form, customer_data)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Get Claim ID
        claim_id = f"C{uuid.uuid4().hex[:8].upper()}"
        
        # Upload files ke Blob Storage
        uploaded_docs = []
        
        # Hospital invoice
        if 'hospitalInvoice' in request.files:
            file = request.files['hospitalInvoice']
            if file.filename:
                doc_id = f"DOC{uuid.uuid4().hex[:8].upper()}"
                blob_name = f"Input_document/invoice/{doc_id}_{file.filename}"
                blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
                blob_client.upload_blob(file.read(), overwrite=True)
                # Save document to CosmosDB
                doc_data = {
                    "id": doc_id,
                    "doc_id": doc_id,
                    "claim_id": claim_id,
                    "doc_type": "invoice",
                    "doc_blob_address": blob_name,
                    "upload_date": datetime.now().isoformat()
                }
                database.get_container_client("document").create_item(doc_data)
                uploaded_docs.append(doc_id)
        # Doctor form
        if 'doctorForm' in request.files:
            file = request.files['doctorForm']
            if file.filename:
                doc_id = f"DOC{uuid.uuid4().hex[:8].upper()}"
                blob_name = f"Input_document/Docform/{doc_id}_{file.filename}"
                blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
                blob_client.upload_blob(file.read(), overwrite=True)
                # Save document ke CosmosDB
                doc_data = {
                    "id": doc_id,
                    "doc_id": doc_id,
                    "claim_id": claim_id,
                    "doc_type": "doctor form",
                    "doc_blob_address": blob_name,
                    "upload_date": datetime.now().isoformat()
                }
                database.get_container_client("document").create_item(doc_data)
                uploaded_docs.append(doc_id)
        # Report Lab
        if 'reportLab' in request.files:
            file = request.files['reportLab']
            if file.filename:
                doc_id = f"DOC{uuid.uuid4().hex[:8].upper()}"
                blob_name = f"Input_document/lab_results/{doc_id}_{file.filename}"
                blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
                blob_client.upload_blob(file.read(), overwrite=True)
                # Save document ke CosmosDB
                doc_data = {
                    "id": doc_id,
                    "doc_id": doc_id,
                    "claim_id": claim_id,
                    "doc_type": "report lab",
                    "doc_blob_address": blob_name,
                    "upload_date": datetime.now().isoformat()
                }
                database.get_container_client("document").create_item(doc_data)
                uploaded_docs.append(doc_id)
        # Additional Document
        if 'additionalDoc' in request.files:
            file = request.files['additionalDoc']
            if file.filename:
                doc_id = f"DOC{uuid.uuid4().hex[:8].upper()}"
                blob_name = f"Input_document/additional_docs/{doc_id}_{file.filename}"
                blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
                blob_client.upload_blob(file.read(), overwrite=True)
                # Save document ke CosmosDB
                doc_data = {
                    "id": doc_id,
                    "doc_id": doc_id,
                    "claim_id": claim_id,
                    "doc_type": "additional doc",
                    "doc_blob_address": blob_name,
                    "upload_date": datetime.now().isoformat()
                }
                database.get_container_client("document").create_item(doc_data)
                uploaded_docs.append(doc_id)
        
        # Save claim ke CosmosDB
        claim_data = {
            "id": claim_id,
            "claim_id": claim_id,
            "customer_id": customer_data[0]['customer_id'],
            "name": customer_data[0]['name'],
            "policy_id": customer_data[0]['policy_id'], 
            "claim_type": claim_type[0]['claim_type'] if isinstance(claim_type, list) else claim_type,
            "claim_amount": float(claim_amount) if claim_amount else 0,
            "currency" : currency, 
            "claim_date": datetime.now().strftime("%d/%m/%Y"),
            "claim_status": "Proses",
            "documents": uploaded_docs,
            "insurance_company": "XYZ Insurance",
            
        }
        
        database.get_container_client("claim").create_item(claim_data)
        
        def run_analysis_async(customer_id, claim_id):
            def target():
                try:
                    analyst_function_executor(customer_id, claim_id)
                except Exception as e:
                    print(f"Error in analyst_function_executor: {e}", file=sys.stderr)
            threading.Thread(target=target).start()
        run_analysis_async(customer_id, claim_id)
        
        return jsonify({
            'status': 'success', 
            'message': 'Claim submitted successfully',
            'claim_id': claim_id,
            'documents_uploaded': len(uploaded_docs)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
@app.route('/api/chatbot', methods=['POST'])
def chatbot_api():
    """Chatbot endpoint for insurance claim officer"""
    try:
        data = request.json
        user_message = data.get('message')
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        try:
            response = Agent_Insurance.run({'input': user_message})
            
            # Extract action_input from JSON response if present
            try:
                import json
                if '"action_input":' in response:
                    # Find the action_input value
                    start = response.find('"action_input": "') + len('"action_input": "')
                    end = response.find('"', start)
                    while response[end-1] == '\\':
                        end = response.find('"', end + 1)
                    clean_response = response[start:end].replace('\\"', '"')
                    return jsonify({'response': clean_response})
            except:
                pass
                
            return jsonify({'response': response})
        except Exception as agent_error:
            print(f"Agent error: {agent_error}")
            return jsonify({'response': 'Maaf, chatbot sedang mengalami gangguan. Silakan coba lagi nanti.'})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)