import json
import sys
import os
import requests
import threading
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import uuid
from datetime import datetime, timedelta
import bcrypt
import jwt
from urllib.parse import urlencode

# Flask
from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from werkzeug.security import check_password_hash # For securely checking passwords

# Azure
from azure.storage.blob import BlobServiceClient,ContentSettings
from azure.cosmos import CosmosClient

# Langchain Functions

from funcHelperApp import cosmos_retrive_data, function_triger, get_content_type
from dotenv import load_dotenv
from chatbotClaimerOfficer import agent 
from doc_intel_for_registration import analize_doc as analize_doc_registration, get_sas_url
import secrets
load_dotenv()
thread_id = uuid.uuid4()
config = {"configurable": {"thread_id": thread_id}}
# Initialize Flask app once
app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://localhost:5174"], "supports_credentials": True}})

app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour in seconds

# Azure setup
blob_connection_string = os.getenv("BLOB_STRING_CONECTION")
if not blob_connection_string:
    raise ValueError("BLOB_STRING_CONECTION environment variable not set")

blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
cosmos_client = CosmosClient(os.getenv("COSMOS_DB_URI"), credential=os.getenv("COSMOS_DB_KEY"))
database = cosmos_client.get_database_client(os.getenv("COSMOS_DB_DATABASE_NAME"))

# Azure Entra ID Configuration
AZURE_CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
AZURE_CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')
AZURE_TENANT_ID = os.getenv('AZURE_TENANT_ID')
AZURE_REDIRECT_URI = os.getenv('AZURE_REDIRECT_URI', 'http://localhost:5000/api/auth/microsoft/callback')
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key')

# File validation for localhost
ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png'}

# Azure Entra ID URLs - Using common endpoint for multi-tenant support
AUTHORIZE_URL = f'https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/authorize'
TOKEN_URL = f'https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/token'
USER_INFO_URL = 'https://graph.microsoft.com/v1.0/me'

def check_session_expired():
    """Check if session is expired"""
    if 'login_time' in session:
        login_time = datetime.fromisoformat(session['login_time'])
        if datetime.now() - login_time > timedelta(seconds=app.config['PERMANENT_SESSION_LIFETIME']):
            session.clear()
            return True
    return False

def validate_file(file):
    """Basic file validation"""
    if not file or not file.filename:
        return False, "No file provided"
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False, f"File type {file_ext} not allowed"
    
    return True, "Valid file"

def run_analysis_async(customer_id, claim_id):
    """Run analysis asynchronously"""
    def target():
        try:
            function_triger(customer_id, claim_id)
        except Exception as e:
            print(f"Error in analyst_function_executor: {e}", file=sys.stderr)
    threading.Thread(target=target, daemon=True).start()

@app.route('/api/analyze-claim', methods=['POST'])
def analyze_claim():
    """Analyze claim using customer_id and claim_id"""
    try:
        data = request.json
        customer_id = data.get('customer_id')
        claim_id = data.get('claim_id')
        
        if not customer_id or not claim_id:
            return jsonify({'error': 'customer_id and claim_id required'}), 400
        
        # Run analysis asynchronously
        run_analysis_async(customer_id, claim_id)
        
        return jsonify({'status': 'success', 'message': 'Analysis started'})
    
    except Exception as e:
        print(f"Error in analyze_claim: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/query', methods=['GET'])
def query_from_cosmosDB():
    """Query data from cosmosDB - Fixed parameter access"""
    try:
        query = request.args.get('query')  # Fixed: use args for GET
        container = request.args.get('container')
        parameter = request.args.get('parameter')
        
        if not query or not container:
            return jsonify({'error': 'query and container required'}), 400
            
        return cosmos_retrive_data(query, container, parameter)
    except Exception as e:
        print(f"Error in query: {e}")
        return jsonify({'error': 'Internal server error'}), 500

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
    
@app.route('/api/signup', methods=['POST'])
def signup():
    """Customer signup with JWT authentication"""
    try:
        data = request.json
        
        # Extract registration data
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Check if customer already exists
        existing_customer = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.email = @email",
            "customer",
            [{"name": "@email", "value": email}]
        )
        
        if existing_customer:
            return jsonify({'error': 'Customer already exists'}), 400
        
        # Check if user is registering as policy holder
        if data.get('isPemegangPolis', True):
            # Check if policy holder already exists for this policy number
            existing_policy_holder = cosmos_retrive_data(
                "SELECT * FROM c WHERE c.policy_no = @policyNo AND c.policyholder_name = @policyHolder",
                "policy",
                [
                    {"name": "@policyNo", "value": data.get('nomorPolis', '')},
                    {"name": "@policyHolder", "value": data.get('namaPemegang', '')}
                ]
            )
            
            if existing_policy_holder:
                return jsonify({'error': 'Policy holder already exists for this policy number'}), 400
        
        # Check if participant number already exists for this policy, card number and insurance company
        existing_participant = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.customer_no = @participantNo AND c.policy_id = @policyId AND c.card_no = @cardNo AND c.insurance_company = @insuranceCompany",
            "customer",
            [
                {"name": "@participantNo", "value": data.get('nomorPeserta', '')},
                {"name": "@policyId", "value": data.get('nomorPolis', '')},
                {"name": "@cardNo", "value": data.get('nomorKartu', '')},
                {"name": "@insuranceCompany", "value": data.get('perusahaanAsuransi', '')}
            ]
        )
        
        if existing_participant:
            return jsonify({'error': 'Participant number already exists for this policy, card number and insurance company', 'field': 'nomorPeserta'}), 400
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Generate customer ID
        customer_id = f"CU{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate age from birth date
        age = None
        dob = data.get('tanggalLahir', '')
        print(f"Received DOB: {dob}")
        if dob:
            try:
                birth_date = datetime.strptime(dob, '%Y-%m-%d')
                age = datetime.now().year - birth_date.year
                if datetime.now().month < birth_date.month or (datetime.now().month == birth_date.month and datetime.now().day < birth_date.day):
                    age -= 1
            except:
                pass
        
        # Map gender
        gender_map = {'laki-laki': 'Male', 'perempuan': 'Female'}
        gender = gender_map.get(data.get('jenisKelamin', ''), '')
        
        # Map marital status
        marital_map = {'menikah': 'Married', 'belum-menikah': 'Single', 'cerai': 'Divorced', 'janda-duda': 'Widowed'}
        marital_status = marital_map.get(data.get('statusPernikahan', ''), '')
        
        # Create customer record
        customer_data = {
            "id": customer_id,
            "customer_id": customer_id,
            "policy_id": data.get('nomorPolis', ''),
            "customer_no": data.get('nomorPeserta', ''),
            "card_no": data.get('nomorKartu', ''),
            "insurance_company": data.get('perusahaanAsuransi', ''),
            "name": data.get('namaPemegang', ''),
            "dob": dob,
            "age": age,
            "gender": gender,
            "NIK": data.get('nik', ''),
            "phone": data.get('nomorTelepon', ''),
            "address": data.get('alamat', ''),
            "email": email,
            "password": password_hash,
            "is_policy_holder": data.get('isPemegangPolis', True),
            "relation_with_policy_holder": "Self" if data.get('isPemegangPolis', True) else data.get('hubungan', ''),
            "employment_status": "",
            "marital_status": marital_status,
            "income": None,
            "claim_id": []
        }
        
        # Save customer to database
        database.get_container_client("customer").create_item(customer_data)
        
        # Check if policy already exists for this policy number
        existing_policy = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.policy_no = @policyNo",
            "policy",
            [{"name": "@policyNo", "value": data.get('nomorPolis', '')}]
        )
        
        if existing_policy:
            # Link to existing policy
            policy_data = existing_policy[0]
        else:
            # Create new policy (only for policy holders)
            if data.get('isPemegangPolis', True):
                policy_data = {
                    "id": f"POL{uuid.uuid4().hex[:8].upper()}",
                    "customer_id": customer_id,  # Only policy holder's customer_id
                    "policy_id": data.get('nomorPolis', ''),
                    "policy_no": data.get('nomorPolis', ''),
                    "policyholder_name": data.get('namaPemegang', ''),
                    "insured_name": data.get('namaPemegang', ''),
                    "start_date": datetime.now().strftime('%Y-%m-%d'),
                    "expire_date": (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'),
                    "insurance_plan_type": data.get('premiumPlan', 'basic'),
                    "total_claim_limit": data.get('claimLimit', ''),
                    "insurance_company": data.get('perusahaanAsuransi', '')
                }
                
                # Save policy to database
                database.get_container_client("policy").create_item(policy_data)
            else:
                return jsonify({'error': 'Policy must be created by policy holder first'}), 400
        
        # Store user data in session
        session['customer_id'] = customer_id
        session['email'] = email
        session['role'] = 'customer'
        session['name'] = customer_data['name']
        session['login_time'] = datetime.now().isoformat()
        session.permanent = True
        
        return jsonify({
            'status': 'success',
            'message': 'Customer and policy registered successfully',
            'user': {
                'id': customer_id,
                'name': customer_data['name'],
                'email': email,
                'role': 'customer'
            },
            'policy': policy_data
        })
        
    except Exception as e:
        print(f"Error in signup: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/signin', methods=['POST'])
def signin():
    """User login"""
    data = request.json
    email = data.get('email', '')
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    # Check user credentials
    user = cosmos_retrive_data(
        "SELECT * FROM c WHERE c.email = @Email",
        "customer",
        [{"name": "@Email", "value": email}]
    )
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401

    user = user[0]
    if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({'error': 'Invalid email or password'}), 401

    # Set default role if not present
    user_role = user.get('role', 'customer')
    
    # Store user data in session
    session['customer_id'] = user['customer_id']
    session['email'] = email
    session['role'] = user_role
    session['name'] = user['name']
    session['login_time'] = datetime.now().isoformat()
    session.permanent = True

    print("-"*10,"User session data:", session)
    return jsonify({
        'status': 'success',
        'message': 'Login successful',
        'user': {
            'id': user['customer_id'],
            'name': user['name'],
            'email': email,
            'role': user_role
        }
    })

@app.route('/api/documents/<doc_id>/download', methods=['GET'])
def download_document(doc_id):
    """Generate secure download URL for document"""
    try:
        # Get document metadata
        doc_data = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.doc_id = @docId",
            "document",
            [{"name": "@docId", "value": doc_id}]
        )
        
        if not doc_data:
            return jsonify({'error': 'Document not found'}), 404
        
        doc = doc_data[0]
        blob_address = doc.get('doc_blob_address')
        
        if not blob_address:
            return jsonify({'error': 'Document file not found'}), 404
        
        # Generate SAS URL for secure download
        from azure.storage.blob import generate_blob_sas, BlobSasPermissions
        from datetime import datetime, timedelta, timezone
        
        account_name = blob_service_client.account_name
        account_key = blob_service_client.credential.account_key
        
        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=container_name,
            blob_name=blob_address,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(minutes=15)  # 15-minute expiry
        )
        
        download_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_address}?{sas_token}"
        
        return jsonify({
            'status': 'success',
            'download_url': download_url,
            'filename': doc.get('doc_type', 'document') + '.pdf',
            'expires_in': 900  # 15 minutes in seconds
        })
        
    except Exception as e:
        print(f"Error generating download URL: {e}")
        return jsonify({'error': 'Failed to generate download URL'}), 500


def safe_fetch_documents(claim_documents):
    """Safely fetch documents with download URLs"""
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
            if doc_data:
                doc = doc_data[0]
                # Add download URL reference
                doc['download_url'] = f"/api/documents/{doc_id}/download"
                documents.append(doc)
            else:
                print(f"Document {doc_id} not found in database")
        except Exception as e:
            print(f"Error fetching document {doc_id}: {e}")
            continue
    
    return documents

@app.route('/api/claims/all-detailed', methods=['GET'])
def get_all_claims_detailed():
    """Get all claims with customer details for approvers"""
    try:
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
            claim['customer_details'] = claim.get('customer_id')
            claim['document_details'] = safe_fetch_documents(claim.get('documents', []))
        
        return jsonify({
            'status': 'success',
            'claims': claims
        })
        
    except Exception as e:
        print(f"Error in get_all_claims_detailed: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/claims/<claim_id>', methods=['GET'])
def get_claim_details(claim_id):
    """Get claim details for editing"""
    try:
        claim_data = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.claim_id = @claimId",
            "claim",
            [{"name": "@claimId", "value": claim_id}]
        )
        if not claim_data:
            return jsonify({'error': 'Claim not found'}), 404

        claim = claim_data[0]
        claim['document_details'] = safe_fetch_documents(claim.get('documents', []))
        
        return jsonify({'status': 'success', 'claim': claim})
        
    except Exception as e:
        print(f"Error getting claim details: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/claims/<claim_id>/update-status', methods=['POST'])
def update_claim_status(claim_id):
    try:
        data = request.json
        status = data.get('status')
        admin_id = data.get('admin_id')
        notes = data.get('notes', '')
        
        if not status or not admin_id:
            return jsonify({'error': 'status and admin_id required'}), 400

        claim_data = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.claim_id = @claimId",
            "claim",
            [{"name": "@claimId", "value": claim_id}]
        )
        if not claim_data:
            return jsonify({'error': 'Claim not found'}), 404

        claim = claim_data[0]
        
        # Check if already processed and not resubmitted
        if claim.get('claim_status') in ['Approved', 'Rejected'] and not claim.get('resubmitted'):
            return jsonify({'error': 'Claim already processed'}), 400
        
        claim['claim_status'] = status
        claim['admin_id'] = admin_id
        if notes == "" :
            claim['admin_notes'] = claim["AI_reasoning"]
        else :
            claim['admin_notes'] = notes
        claim['processed_date'] = datetime.now().isoformat()
        claim['resubmitted'] = False  # Reset resubmission flag
        claim['approved_by'] = admin_id
        claim['approved_date'] = datetime.now().isoformat()
        updated_claim = database.get_container_client("claim").upsert_item(claim)
        
        try:
            function_triger(claim['customer_id'], claim_id, admin_id)
        except Exception as e:
            print(f"Function trigger error: {e}")

        return jsonify({'status': 'success', 'claim': updated_claim})
        
    except Exception as e:
        print(f"Error updating claim status: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/customer/<customer_id>/claims-detailed', methods=['GET'])
def get_customer_claims_detailed(customer_id):
    """Get detailed claims for a specific customer with documents"""
    try:
        # Check if user is logged in
        if 'customer_id' not in session or check_session_expired():
            return jsonify({'error': 'Authentication required'}), 401
        
        customer_id = session['customer_id']
        user_role = session.get('role')

        if user_role != 'customer':
            return jsonify({'error': 'Access forbidden: Customers only'}), 403

        claims = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.customer_id = @customerId ORDER BY c._ts DESC", 
            "claim", 
            [{"name": "@customerId", "value": customer_id}]
        )
        
        for claim in claims:
            claim['document_details'] = safe_fetch_documents(claim.get('documents', []))
        
        return jsonify({
            'status': 'success',
            'claims': claims
        })
        
    except Exception as e:
        print(f"Error in get_customer_claims_detailed: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def validate_customer_data(form_data, customer_data):
    """Validate form data against database customer record"""
    if not customer_data:
        return False, "Customer not found in database"
    
    customer = customer_data[0]
    form_customer_id = form_data.get('customerId')
    form_policy_id = form_data.get('policyId')
    print(f"Validating customer ID: form {form_customer_id} vs db {customer['customer_id']}")
    
    if customer['customer_id'] != form_customer_id:
        return False, "Customer ID mismatch"
    
    if customer['policy_id'] != form_policy_id:
        return False, "Policy ID mismatch"
    
    return True, "Valid customer"


@app.route('/api/customer-claim-history/<customer_id>', methods=['GET'])
def get_customer_claim_history(customer_id):
    """Get claim history for a specific customer with hospital names from invoices"""
    try:
        print (f"Session data: {session}")
        if 'customer_id' not in session or check_session_expired():
            return jsonify({'error': 'Authentication required'}), 401
        
        user_role = session.get('role')
        if user_role != 'customer':
            return jsonify({'error': 'Access forbidden: Customers only'}), 403
        
        # Verify customer can only access their own data
        session_customer_id = session['customer_id']
        if customer_id != session_customer_id:
            return jsonify({'error': 'Access forbidden: Can only access own data'}), 403

        claims = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.customer_id = @customerId ORDER BY c._ts DESC", 
            "claim", 
            [{"name": "@customerId", "value": customer_id}]
        )
        
        for claim in claims:
            hospital_name = "Unknown Hospital"
            
            if claim.get('documents'):
                for doc_id in claim['documents']:
                    try:
                        doc_data = cosmos_retrive_data(
                            "SELECT * FROM c WHERE c.doc_id = @docId AND c.doc_type = 'invoice'", 
                            "document", 
                            [{"name": "@docId", "value": doc_id}]
                        )
                        
                        if doc_data:
                            doc = doc_data[0]
                            if doc.get('doc_contents'):
                                if doc['doc_contents'].get('Invoice #1'):
                                    vendor_name = doc['doc_contents']['Invoice #1'].get('Vendor Name')
                                    if vendor_name:
                                        hospital_name = vendor_name.replace('\n', ' ').strip()
                                        break
                    except Exception as doc_error:
                        print(f"Error fetching document {doc_id}: {doc_error}")
                        continue
            
            claim['hospitalName'] = hospital_name
        
        return jsonify({
            'status': 'success',
            'claims': claims
        })
        
    except Exception as e:
        print(f"Error in get_customer_claim_history: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/submit-claim', methods=['POST'])
def submit_claim():
    """Submit or update claim form with file uploads"""
    try:
        # Check if user is logged in
        if 'customer_id' not in session or check_session_expired():
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check if this is an edit
        is_edit = request.form.get('isEdit') == 'true'
        existing_claim_id = request.form.get('claimId') if is_edit else None
        
        # Get form data
        claim_type = request.form.get('claimType')
        claim_amount = request.form.get('claimAmount')
        currency = request.form.get('currency')
        customer_id = request.form.get('customerId')

        # Get customer_id from session
        customer_id = session['customer_id']

        policy_id = request.form.get('policyId')
        date_checkin = request.form.get('treatmentStartDate')
        date_checkout = request.form.get('treatmentEndDate')
        insurance_company = request.form.get('insuranceCompany')
        
        # Validate claim amount
        try:
            claim_amount_float = float(claim_amount) if claim_amount else 0
            if claim_amount_float <= 0:
                return jsonify({'error': 'Invalid claim amount'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid claim amount format'}), 400
        
        # Check claim limit for new claims
        if not is_edit:
            policy_data = cosmos_retrive_data(
                "SELECT * FROM c WHERE c.policy_no = @policyNo",
                "policy",
                [{"name": "@policyNo", "value": policy_id}]
            )
            
            if policy_data:
                policy_limit = policy_data[0].get('total_claim_limit', 0)
                
                # Get approved claims for this year
                current_year = datetime.now().year
                approved_claims = cosmos_retrive_data(
                    "SELECT * FROM c WHERE c.customer_id = @customerId AND c.claim_status = 'Approved' AND STARTSWITH(c.claim_date, @year)",
                    "claim",
                    [
                        {"name": "@customerId", "value": customer_id},
                        {"name": "@year", "value": str(current_year)}
                    ]
                )
                
                total_approved = sum(float(claim.get('claim_amount', 0)) for claim in approved_claims)
                
                if total_approved + claim_amount_float > policy_limit:
                    return jsonify({
                        'error': f'Claim amount exceeds annual limit. Used: Rp {total_approved:,.0f}, Limit: Rp {policy_limit:,.0f}'
                    }), 400
        
        # Get customer data
        customer_data = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.customer_id = @customerId", 
            "customer", 
            [{"name": "@customerId", "value": customer_id}]
        )
        
        is_valid, message = validate_customer_data(request.form, customer_data)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        if is_edit:
            # Get existing claim
            claim_data = cosmos_retrive_data(
                "SELECT * FROM c WHERE c.claim_id = @claimId",
                "claim",
                [{"name": "@claimId", "value": existing_claim_id}]
            )
            if not claim_data or claim_data[0]['claim_status'] != 'Rejected':
                return jsonify({'error': 'Can only edit rejected claims'}), 400
            
            claim = claim_data[0]
            claim_id = existing_claim_id
            uploaded_docs = claim.get('documents', [])
        else:
            claim_id = f"C{uuid.uuid4().hex[:8].upper()}"
            uploaded_docs = []
        
        # Process file uploads with validation
        file_mappings = {
            'hospitalInvoice': ('invoice', 'Input_document/invoice/'),
            'doctorForm': ('doctor form', 'Input_document/Docform/'),
            'reportLab': ('report lab', 'Input_document/lab_results/'),
            'additionalDoc': ('additional doc', 'Input_document/additional_docs/')
        }
        
        for form_field, (doc_type, blob_path) in file_mappings.items():
            if form_field in request.files:
                file = request.files[form_field]
                if file.filename:
                    # Validate file
                    is_valid, message = validate_file(file)
                    if not is_valid:
                        return jsonify({'error': f'{form_field}: {message}'}), 400
                    
                    doc_id = f"DOC{uuid.uuid4().hex[:8].upper()}"
                    blob_name = f"{blob_path}{doc_id}_{file.filename}"
                    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
                    content_type = get_content_type(file)
                    blob_client.upload_blob(file.read(), overwrite=True, content_settings=ContentSettings(content_type=content_type))
                    print(f"Uploaded {form_field} to {blob_name} with content type {content_type}")
                    doc_data = {
                        "id": doc_id,
                        "doc_id": doc_id,
                        "claim_id": claim_id,
                        "doc_type": doc_type,
                        "doc_blob_address": blob_name,
                        "upload_date": datetime.now().isoformat()
                    }
                    database.get_container_client("document").create_item(doc_data)
                    uploaded_docs.append(doc_id)
        
        # Check if claim exceeds limit (for approver warning)
        exceeds_limit = False
        limit_info = {}
        
        policy_data = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.policy_no = @policyNo",
            "policy",
            [{"name": "@policyNo", "value": customer_data[0]['policy_id']}]
        )
        
        if policy_data:
            policy_limit = policy_data[0].get('total_claim_limit', 0)
            current_year = datetime.now().year
            approved_claims = cosmos_retrive_data(
                "SELECT * FROM c WHERE c.customer_id = @customerId AND c.claim_status = 'Approved' AND STARTSWITH(c.claim_date, @year)",
                "claim",
                [
                    {"name": "@customerId", "value": customer_id},
                    {"name": "@year", "value": str(current_year)}
                ]
            )
            
            total_approved = sum(float(claim.get('claim_amount', 0)) for claim in approved_claims)
            
            if total_approved + claim_amount_float > policy_limit:
                exceeds_limit = True
                limit_info = {
                    'total_used': total_approved,
                    'policy_limit': policy_limit,
                    'current_claim': claim_amount_float,
                    'would_exceed_by': (total_approved + claim_amount_float) - policy_limit
                }
        
        # Save or update claim
        claim_data = {
            "id": claim_id,
            "claim_id": claim_id,
            "customer_id": customer_data[0]['customer_id'],
            "name": customer_data[0]['name'],
            "policy_id": customer_data[0]['policy_id'], 
            "claim_type": claim_type,
            "claim_amount": claim_amount_float,
            "currency": currency, 
            "claim_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "claim_status": "Proses",
            "documents": uploaded_docs,
            "insurance_company": insurance_company,
            "date_checkin": date_checkin,
            "date_checkout": date_checkout,
            "resubmitted": is_edit,  # Mark as resubmitted if editing
            "exceeds_limit": exceeds_limit,
            "limit_info": limit_info if exceeds_limit else None
        }
        
        database.get_container_client("claim").upsert_item(claim_data)
        run_analysis_async(customer_id, claim_id)
        
        return jsonify({
            'status': 'success', 
            'message': 'Claim updated successfully' if is_edit else 'Claim submitted successfully',
            'claim_id': claim_id,
            'documents_uploaded': len(uploaded_docs)
        })
    
    except Exception as e:
        print(f"Error submitting claim: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/chatbot', methods=['POST'])
def chatbot_api():
    """Chatbot endpoint for insurance claim officer"""
    try:
        data = request.json
        user_message = data.get('message')
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400

        # Ensure user_message is a valid string
        user_message = str(user_message)

        print(f"User message: {user_message}")

        # Ensure that the message is in the correct format
        formatted_input = {
            "messages": [{"role": "user", "content": user_message}]
        }

        try:
            response = ''
            for chunk in agent.stream(input=formatted_input, config=config, stream_mode="values"):
                response = chunk   # i just want the AI Final answer
                print(f"AI response: {response}")
            response = response['messages'][-1].content  
            response = str(response)
            return jsonify({'response': response})
        except Exception as agent_error:
            print(f"Agent error: {agent_error}")
            return jsonify({'response': 'Maaf, chatbot sedang mengalami gangguan. Silakan coba lagi nanti.'}), 500

    except Exception as e:
        print(f"Error in chatbot: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/customer/profile', methods=['GET'])
def get_customer_profile():
    """Get customer profile data"""
    try:
        if 'customer_id' not in session or check_session_expired():
            return jsonify({'error': 'Authentication required'}), 401        
        customer_id = session['customer_id']
        customer_data = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.customer_id = @customerId",
            "customer",
            [{"name": "@customerId", "value": customer_id}]
        )
        
        if not customer_data:
            return jsonify({'error': 'Customer not found'}), 404
            
        return jsonify({
            'status': 'success',
            'customer': customer_data[0]
        })
        
    except Exception as e:
        print(f"Error getting customer profile: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/customer/<customer_id>/policy', methods=['GET'])
def get_customer_policy(customer_id):
    """Get customer policy data"""
    try:
        if 'customer_id' not in session or check_session_expired():
            return jsonify({'error': 'Authentication required'}), 401
        
        if session['customer_id'] != customer_id:
            return jsonify({'error': 'Access forbidden'}), 403
        
        # Get customer data first
        customer_data = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.customer_id = @customerId",
            "customer",
            [{"name": "@customerId", "value": customer_id}]
        )
        
        if not customer_data:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Get policy data by policy_no (shared across all users with same policy)
        policy_data = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.policy_no = @policyNo",
            "policy",
            [{"name": "@policyNo", "value": customer_data[0]['policy_id']}]
        )
        
        if not policy_data:
            return jsonify({'error': 'Policy not found'}), 404
            
        return jsonify({
            'status': 'success',
            'policy': policy_data[0]
        })
        
    except Exception as e:
        print(f"Error getting customer policy: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/customer/<customer_id>/policy-limits', methods=['GET'])
def get_customer_policy_limits(customer_id):
    """Get customer policy limits and usage for approvers"""
    try:
        # Get customer data
        customer_data = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.customer_id = @customerId",
            "customer",
            [{"name": "@customerId", "value": customer_id}]
        )
        
        if not customer_data:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Get policy data
        policy_data = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.policy_no = @policyNo",
            "policy",
            [{"name": "@policyNo", "value": customer_data[0]['policy_id']}]
        )
        
        if not policy_data:
            return jsonify({'error': 'Policy not found'}), 404
        
        policy_limit = policy_data[0].get('total_claim_limit', 0)
        
        # Get approved claims for current year
        current_year = datetime.now().year
        approved_claims = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.customer_id = @customerId AND c.claim_status = 'Approved' AND STARTSWITH(c.claim_date, @year)",
            "claim",
            [
                {"name": "@customerId", "value": customer_id},
                {"name": "@year", "value": str(current_year)}
            ]
        )
        
        total_used = sum(float(claim.get('claim_amount', 0)) for claim in approved_claims)
        
        return jsonify({
            'status': 'success',
            'policy_limit': policy_limit,
            'total_used': total_used,
            'remaining': policy_limit - total_used,
            'year': current_year
        })
        
    except Exception as e:
        print(f"Error getting policy limits: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/update-claim', methods=['POST'])
def update_claim():
    """Update claim details"""
    try:
        data = request.json
        claim_id = data.get('claim_id')
        status = data.get('status')
        admin_id = data.get('admin_id')
        notes = data.get('notes', '')

        if not claim_id or not status or not admin_id:
            return jsonify({'error': 'claim_id, status, and admin_id required'}), 400

        claim_data = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.claim_id = @claimId",
            "claim",
            [{"name": "@claimId", "value": claim_id}]
        )
        if not claim_data:
            return jsonify({'error': 'Claim not found'}), 404

        claim = claim_data[0]
        claim['claim_status'] = status
        claim['admin_id'] = admin_id
        claim['admin_notes'] = notes
        claim['processed_date'] = datetime.now().isoformat()
        
        if status == 'Rejected':
            claim['rejected_by'] = admin_id
            claim['rejected_date'] = datetime.now().isoformat()
        elif status == 'Approved':
            claim['approved_by'] = admin_id
            claim['approved_date'] = datetime.now().isoformat()

        updated_claim = database.get_container_client("claim").upsert_item(claim)
        return jsonify({'status': 'success', 'claim': updated_claim})

    except Exception as e:
        print(f"Error updating claim: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/extract-registration-info', methods=['POST'])
def extract_registration_info():
    """Extract information from uploaded documents for registration"""
    try:
        extracted_data = {}
        
        # Process insurance card - upload
        if 'insurance_card' in request.files:
            file = request.files['insurance_card']
            if file.filename:
                doc_id = f"REG{uuid.uuid4().hex[:8].upper()}"
                blob_name = f"registration/{doc_id}_{file.filename}"
                blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
                blob_client.upload_blob(file.read(), overwrite=True)
                print(f"Insurance card uploaded: {blob_name}")
                
                # Extract insurance card data
                insurance_data = analize_doc_registration(blob_name, "insuranceCard")
                print(f"Insurance card extraction result: {insurance_data}")
                if insurance_data and not insurance_data.get('error'):
                    extracted_data.update({
                        'policy_number': insurance_data.get('No. Polis', ''),
                        'participant_number': insurance_data.get('No. Peserta', ''),
                        'card_number': insurance_data.get('No. Kartu', '')
                    })
        
        # Process ID card with Azure Document Intelligence
        if 'id_card' in request.files:
            file = request.files['id_card']
            if file.filename:
                doc_id = f"REG{uuid.uuid4().hex[:8].upper()}"
                blob_name = f"registration/{doc_id}_{file.filename}"
                blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
                blob_client.upload_blob(file.read(), overwrite=True)
                
                # Extract using Azure Document Intelligence with fallback
                id_data = analize_doc_registration(blob_name, "idCard")
                print(f"ID card extraction result: {id_data}")
                
                # Map ID card data to expected format
                if id_data:
                    extracted_data.update({
                        'nik': id_data.get('NIK', ''),
                        'full_name': id_data.get('Nama', ''),
                        'birth_date': id_data.get('Tempat/Tgl Lahir', ''),
                        'gender': id_data.get('Jenis Kelamin', ''),
                        'address': id_data.get('Alamat', ''),
                        'rt_rw': id_data.get('RT/RW', ''),
                        'kelurahan': id_data.get('Kel/Desa', ''),
                        'kecamatan': id_data.get('Kecamatan', ''),
                        'marital_status': id_data.get('Status Perkawinan', ''),
                        'occupation': id_data.get('Pekerjaan', '')
                    })
        return jsonify({
            'status': 'success',
            'data': extracted_data
        })
    
    except Exception as e:
        print(f"Error in document extraction: {e}")
        return jsonify({'error': 'Document processing failed'}), 500

@app.route('/api/validate-participant', methods=['POST'])
def validate_participant():
    """Validate participant number uniqueness"""
    try:
        data = request.json
        
        existing_participant = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.customer_no = @participantNo AND c.policy_id = @policyId AND c.card_no = @cardNo AND c.insurance_company = @insuranceCompany",
            "customer",
            [
                {"name": "@participantNo", "value": data.get('nomorPeserta', '')},
                {"name": "@policyId", "value": data.get('nomorPolis', '')},
                {"name": "@cardNo", "value": data.get('nomorKartu', '')},
                {"name": "@insuranceCompany", "value": data.get('perusahaanAsuransi', '')}
            ]
        )
        
        if existing_participant:
            return jsonify({'error': 'Participant number already exists', 'field': 'nomorPeserta'}), 400
            
        return jsonify({'status': 'valid'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

@app.route('/api/documents/<doc_id>', methods=['GET'])
def get_document_metadata(doc_id):
    try:
        # Query Cosmos DB for document metadata
        query = f"SELECT * FROM c WHERE c.doc_id = @docId"
        items = cosmos_retrive_data(query, "document",[{"name": "@docId", "value": doc_id}])
        if not items:
            return jsonify({"error": "Document not found"}), 404
        document = items[0]
        # Construct the full URL for the document
        blob_path = document['doc_blob_address']
        document_url = get_sas_url(blob_path)
        # Add the document URL to the response
        document['doc_url'] = document_url
        return jsonify(document)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/session-status', methods=['GET'])
def session_status():
    """Check session status"""
    print(f"Session data: {dict(session)}")
    print(f"Session expired: {check_session_expired()}")
    
    if ('customer_id' in session or 'admin_id' in session) and not check_session_expired():
        return jsonify({
            'status': 'authenticated',
            'user': {
                'id': session.get('customer_id') or session.get('admin_id'),
                'customer_id': session.get('customer_id'),
                'admin_id': session.get('admin_id'),
                'email': session.get('email'),
                'role': session.get('role'),
                'name': session.get('name')
            }
        })
    else:
        print("Session not authenticated or expired")
        return jsonify({'status': 'not_authenticated'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    """User logout"""
    print("Logging out user...")
    print(f"Session before clear: {dict(session)}")
    session.clear()
    session.permanent = False
    return jsonify({'status': 'success', 'message': 'Logged out successfully'})


@app.route('/api/auth/microsoft', methods=['GET'])
def microsoft_auth():
    """Redirect to Microsoft Entra ID for authentication"""
    state = str(uuid.uuid4())
    session['oauth_state'] = state
    
    params = {
        'client_id': AZURE_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': AZURE_REDIRECT_URI,
        'response_mode': 'query',
        'scope': 'openid profile email User.Read',
        'state': state
    }
    
    auth_url = f"{AUTHORIZE_URL}?{urlencode(params)}"
    print(f"Generated auth URL: {auth_url}")
    print(f"Redirect URI: {AZURE_REDIRECT_URI}")
    return redirect(auth_url)

@app.route('/api/auth/microsoft/callback', methods=['GET'])
def microsoft_callback():
    """Handle Microsoft Entra ID callback"""
    try:
        # Debug: Print all query parameters
        print(f"Callback received parameters: {dict(request.args)}")
        print(f"Session oauth_state: {session.get('oauth_state')}")
        
        # Check for error in callback
        error = request.args.get('error')
        if error:
            error_desc = request.args.get('error_description', 'Unknown error')
            print(f"OAuth error: {error} - {error_desc}")
            return redirect(f'http://localhost:5173/signin?error={error}')
        
        # Verify state parameter
        if request.args.get('state') != session.get('oauth_state'):
            return redirect('http://localhost:5173/signin?error=invalid_state')
        
        # Get authorization code
        code = request.args.get('code')
        if not code:
            print("No authorization code received")
            return redirect('http://localhost:5173/signin?error=no_code')
        
        # Exchange code for token
        token_data = {
            'client_id': AZURE_CLIENT_ID,
            'client_secret': AZURE_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': AZURE_REDIRECT_URI,
            'scope': 'openid profile email User.Read'
        }
        
        token_response = requests.post(TOKEN_URL, data=token_data)
        print(f"Token response status: {token_response.status_code}")
        print(f"Token response: {token_response.text}")
        
        if token_response.status_code != 200:
            return redirect('http://localhost:5173/signin?error=token_request_failed')
            
        token_json = token_response.json()
        
        if 'access_token' not in token_json:
            error_desc = token_json.get('error_description', 'Unknown error')
            print(f"Token error: {error_desc}")
            return redirect('http://localhost:5173/signin?error=token_failed')
        
        # Get user info from Microsoft Graph
        headers = {'Authorization': f"Bearer {token_json['access_token']}"}
        user_response = requests.get(USER_INFO_URL, headers=headers)
        user_data = user_response.json()
        
        email = user_data.get('mail') or user_data.get('userPrincipalName')
        if not email:
            return redirect('http://localhost:5173/signin?error=no_email')
        
        # Check if email exists in insurance_admin container
        admin_user = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.email = @email",
            "insurance_admin",
            [{"name": "@email", "value": email}]
        )
        
        if not admin_user:
            return redirect('http://localhost:5173/signin?error=user_not_found')
        
        admin = admin_user[0]
        
        # Set session with insurance_admin data and role as approver
        session['customer_id'] = admin.get('admin_id', admin.get('id'))
        session['email'] = admin['email']
        session['role'] = 'approver'
        session['name'] = admin['name']
        session['admin_id'] = admin.get('admin_id', admin.get('id'))
        session['login_time'] = datetime.now().isoformat()
        session.permanent = True
        
        print(f"Session set successfully: {dict(session)}")
        print(f"Session permanent: {session.permanent}")
        
        # Redirect to signin page, frontend will check session and handle redirect
        return redirect('http://localhost:5173/signin')
        
    except Exception as e:
        print(f"Microsoft auth error: {e}")
        return redirect('http://localhost:5173/signin?error=auth_failed')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)