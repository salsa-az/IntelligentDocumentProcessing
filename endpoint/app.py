import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from datetime import datetime
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient
from stepfunc import analyst_function_executor
from doc_intel import analize_doc
from analyst_tools import cosmos_retrive_data
from dotenv import load_dotenv

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

@app.route('/api/extract-document', methods=['POST'])
def extract_document():
    """Extract document using blob address and model type"""
    try:
        data = request.json
        blob_address = data.get('blob_address')
        model_type = data.get('model_type', 'prebuilt-invoice')
        
        if not blob_address:
            return jsonify({'error': 'blob_address required'}), 400
        
        # Extract document
        result = analize_doc(blob_address, model_type)
        
        return jsonify({'status': 'success', 'data': result})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-claims', methods=['GET'])
def get_claims():
    """Get all claims from database"""
    try:
        claims = cosmos_retrive_data("SELECT * FROM c", "claim")
        return jsonify({'status': 'success', 'data': claims})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-claim/<claim_id>', methods=['GET'])
def get_claim(claim_id):
    """Get specific claim by ID"""
    try:
        claim = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.claim_id = @id", 
            "claim", 
            parameters=[{"name": "@id", "value": claim_id}]
        )
        
        if not claim:
            return jsonify({'error': 'Claim not found'}), 404
        
        return jsonify({'status': 'success', 'data': claim[0]})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/submit-claim', methods=['POST'])
def submit_claim():
    """Submit claim form with file uploads"""
    try:
        # Get form data
        claim_type = request.form.get('claimType')
        claim_amount = request.form.get('claimAmount')
        currency = request.form.get('currency')
        customer_id = request.form.get('customerId', 'CU001')  # Default for now
        
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
                blob_name = f"{doc_id}_{file.filename}"
                blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
                blob_client.upload_blob(file.read(), overwrite=True)
                
                # Save document ke CosmosDB
                doc_data = {
                    "id": doc_id,
                    "doc_id": doc_id,
                    "claim_id": claim_id,
                    "doc_type": "doctor_form",
                    "doc_blob_address": blob_name,
                    "upload_date": datetime.now().isoformat()
                }
                database.get_container_client("document").create_item(doc_data)
                uploaded_docs.append(doc_id)
        
        # Save claim ke CosmosDB
        claim_data = {
            "id": claim_id,
            "claim_id": claim_id,
            "customer_id": customer_id,
            "policy_id": "P001",  # Default policy ID
            "admin_id": 3001,  # Default admin ID
            "claim_type": claim_type,
            "claim_amount": float(claim_amount) if claim_amount else 0,
            "claim_date": datetime.now().strftime("%d/%m/%Y"),
            "claim_status": "Proses",
            "documents": uploaded_docs,
            "insurance_company": "PT Asuransi Terpercaya",
            "summary": "",
            "AI_suggestion": "",
            "AI_reasoning": ""
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
