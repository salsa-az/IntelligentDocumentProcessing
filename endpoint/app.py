import sys
import os
import requests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from datetime import datetime
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient
# from IntelegentDocumentProcecing.endpoint.analyst_func import analyst_function_executor
from endpoint.analyst_func import analyst_function_executor
from doc_intel import analize_doc
from analyst_tools import cosmos_retrive_data
from dotenv import load_dotenv
from letterfunc import letter_chain_pro

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
        letter_chain_pro(customer_data, claim_data, policy_data, admin_data)
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
        


@app.route('/api/submit-claim', methods=['POST'])
def submit_claim():
    """Submit claim form with file uploads"""
    try:
        # Get form data
        claim_type = request.form.get('claimType')
        claim_amount = request.form.get('claimAmount')
        currency = request.form.get('currency')
        customer_id = request.form.get('customerId')  # Default for now
        policy_id = request.form.get('policyId')
        
        # Generate IDs
        claim_id = f"C{uuid.uuid4().hex[:8].upper()}"
        
        # Upload files ke Blob Storage
        uploaded_docs = []
        
        # Hospital invoice
        if 'hospitalInvoice' in request.files:
            file = request.files['hospitalInvoice']
            if file.filename:
                doc_id = f"DOC{uuid.uuid4().hex[:8].upper()}"
                blob_name = f"{doc_id}_{file.filename}"
                blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
                blob_client.upload_blob(file.read(), overwrite=True)
                
                # Save document to CosmosDB
                doc_data = {
                    "id": doc_id,
                    "doc_id": doc_id,
                    "claim_id": claim_id,
                    "doc_type": "invoice",
                    "doc_blob_address": "Input_document/invoice/"+ blob_name,
                    "upload_date": datetime.now().isoformat()
                }
                database.get_container_client("document").create_item(doc_data)
                uploaded_docs.append(doc_id)
        
        # Doctor form
        if 'doctorForm' in request.files:
            file = request.files['doctorForm']
            if file.filename:
                doc_id = f"DOC{uuid.uuid4().hex[:8].upper()}"
                blob_name = f"{doc_id}_{file.filename}"
                blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
                blob_client.upload_blob(file.read(), overwrite=True)
                
                # Save document ke CosmosDB
                doc_data = {
                    "id": doc_id,
                    "doc_id": doc_id,
                    "claim_id": claim_id,
                    "doc_type": "doctor_form",
                    "doc_blob_address": "Input_document/Docform/"+blob_name,
                    "upload_date": datetime.now().isoformat()
                }
                database.get_container_client("document").create_item(doc_data)
                uploaded_docs.append(doc_id)
        
        # Save claim ke CosmosDB
        claim_data = {
            "id": claim_id,
            "claim_id": claim_id,
            "customer_id": customer_id,
            "policy_id": policy_id, 
            "claim_type": claim_type,
            "claim_amount": float(claim_amount) if claim_amount else 0,
            "currency" : currency, 
            "claim_date": datetime.now().strftime("%d/%m/%Y"),
            "claim_status": "Proses",
            "documents": uploaded_docs,
            "insurance_company": "XYZ Insurance"
        }
        
        database.get_container_client("claim").create_item(claim_data)
        
        return jsonify({
            'status': 'success', 
            'message': 'Claim submitted successfully',
            'claim_id': claim_id,
            'documents_uploaded': len(uploaded_docs)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)