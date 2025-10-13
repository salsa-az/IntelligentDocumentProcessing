import sys
import os
import requests
import threading
import uuid
import json
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import bcrypt
import jwt
from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask import send_from_directory, send_file
from werkzeug.security import check_password_hash
from azure.storage.blob import BlobServiceClient, ContentSettings, generate_blob_sas, BlobSasPermissions
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from funcHelperApp import cosmos_retrive_data, function_triger, get_content_type
from chatbotClaimerOfficer import agent 
from doc_intel_for_registration import analize_doc as analize_doc_registration, get_sas_url

# =============================================================================
# CONFIGURATION
# =============================================================================
load_dotenv()

app = Flask(__name__)
# Production CORS configuration
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5000", 
    "http://localhost:5000",
    "https://idp-insurance.azurewebsites.net",
    "idp-insurance-g0crawavdnaggthj.southeastasia-01.azurewebsites.net/",
    "https://*.azurewebsites.net"
]

# Enhanced CORS configuration
CORS(app, resources={
    r"/api/*": {
        "origins": allowed_origins, 
        "supports_credentials": True,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
    }
})

# Enhanced session configuration
is_production = os.getenv('FLASK_ENV') == 'production' or os.getenv('WEBSITE_HOSTNAME') is not None
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_COOKIE_SECURE'] = is_production
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'None' if is_production else 'Lax'
app.config['SESSION_COOKIE_DOMAIN'] = None
app.config['SESSION_COOKIE_NAME'] = 'idp_session'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600

# Azure setup
blob_connection_string = os.getenv("BLOB_STRING_CONECTION")
if not blob_connection_string:
    raise ValueError("BLOB_STRING_CONECTION environment variable not set")

blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
cosmos_client = CosmosClient(os.getenv("COSMOS_DB_URI"), credential=os.getenv("COSMOS_DB_KEY"))
database = cosmos_client.get_database_client(os.getenv("COSMOS_DB_DATABASE_NAME"))

# Azure Entra ID
AZURE_CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
AZURE_CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')
AZURE_TENANT_ID = os.getenv('AZURE_TENANT_ID')

JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key')

# Constants
ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png'}
AUTHORIZE_URL = f'https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/authorize'
TOKEN_URL = f'https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/token'
USER_INFO_URL = 'https://graph.microsoft.com/v1.0/me'

# Chatbot
thread_id = uuid.uuid4()
config = {"configurable": {"thread_id": thread_id}}

# =============================================================================
# SERVE STATIC FILES
# =============================================================================
@app.route('/')
def serve_frontend():
    try:
        return send_from_directory('dist', 'index.html')
    except:
        return jsonify({'message': 'Frontend not built. Run: cd frontend && npm run build && cd .. && mv frontend/dist dist'}), 404

@app.route('/<path:path>')
def serve_static(path):
    if path.startswith('api/'):
        return jsonify({'error': 'API endpoint not found'}), 404
    try:
        return send_from_directory('dist', path)
    except:
        try:
            return send_from_directory('dist', 'index.html')
        except:
            return jsonify({'message': 'Frontend not built'}), 404


# =============================================================================
# UTILITY
# =============================================================================
@app.route('/api/query', methods=['GET'])
def query_from_cosmosDB():
    try:
        query = request.args.get('query')
        container = request.args.get('container')
        parameter = request.args.get('parameter')
        
        if not query or not container:
            return jsonify({'error': 'query and container required'}), 400
            
        return cosmos_retrive_data(query, container, parameter)
    except Exception as e:
        print(f"Error in query: {e}")
        return jsonify({'error': 'Internal server error'}), 500


def check_session_expired():
    if 'login_time' in session:
        login_time = datetime.fromisoformat(session['login_time'])
        if datetime.now() - login_time > timedelta(seconds=app.config['PERMANENT_SESSION_LIFETIME']):
            session.clear()
            return True
    return False

def validate_file(file):
    if not file or not file.filename:
        return False, "No file provided"
    
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False, f"File type {file_ext} not allowed"
    
    # Check file size (10MB limit)
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    if file_size > 10 * 1024 * 1024:  # 10MB
        return False, "File size exceeds 10MB limit"
    
    return True, "Valid file"

def run_analysis_async(customer_id, claim_id):
    def target():
        try:
            function_triger(customer_id, claim_id)
        except Exception as e:
            print(f"Error in analyst_function_executor: {e}", file=sys.stderr)
    threading.Thread(target=target, daemon=True).start()

def safe_fetch_documents(claim_documents):
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
                doc['download_url'] = f"/api/documents/{doc_id}/download"
                documents.append(doc)
        except Exception as e:
            print(f"Error fetching document {doc_id}: {e}")
            continue
    return documents

def validate_customer_data(form_data, customer_data):
    if not customer_data:
        return False, "Customer not found in database"
    customer = customer_data[0]
    form_customer_id = form_data.get('customerId')
    form_policy_id = form_data.get('policyId')
    if customer['customer_id'] != form_customer_id:
        return False, "Customer ID mismatch"
    if customer['policy_id'] != form_policy_id:
        return False, "Policy ID mismatch"
    return True, "Valid customer"

# =============================================================================
# AUTHENTICATION ROUTES
# =============================================================================
@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        existing_customer = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.email = @email",
            "customer",
            [{"name": "@email", "value": email}]
        )
        
        if existing_customer:
            return jsonify({'error': 'Customer already exists'}), 400
        
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        customer_id = f"CU{uuid.uuid4().hex[:8].upper()}"
        
        # Policy validation
        policy_id = request.form.get('nomorPolis', '')
        participant_no = request.form.get('nomorPeserta', '')
        
        if policy_id and participant_no:
            existing_participant = cosmos_retrive_data(
                "SELECT * FROM c WHERE c.customer_no = @participantNo",
                "customer",
                [{"name": "@participantNo", "value": participant_no}]
            )
            
            if existing_participant:
                return jsonify({'error': 'Participant number already exists', 'field': 'nomorPeserta'}), 400
            
            existing_policy_holder = cosmos_retrive_data(
                "SELECT * FROM c WHERE c.policy_id = @policyId AND c.is_policy_holder = true",
                "customer",
                [{"name": "@policyId", "value": policy_id}]
            )
            
            if existing_policy_holder:
                policy_holder = existing_policy_holder[0]
                policy_holder_name = policy_holder.get('name', '')
            else:
                policy_holder_name = request.form.get('namaPemegang', '')
        else:
            policy_holder_name = request.form.get('namaPemegang', '')
        
        # Age calculation
        age = None
        dob = request.form.get('tanggalLahir', '')
        if dob:
            try:
                birth_date = datetime.strptime(dob, '%Y-%m-%d')
                age = datetime.now().year - birth_date.year
                if datetime.now().month < birth_date.month or (datetime.now().month == birth_date.month and datetime.now().day < birth_date.day):
                    age -= 1
            except:
                pass
        
        # Mappings
        gender_map = {'laki-laki': 'Male', 'perempuan': 'Female'}
        gender = gender_map.get(request.form.get('jenisKelamin', ''), '')
        
        marital_map = {'menikah': 'Married', 'belum-menikah': 'Single', 'cerai': 'Divorced', 'janda-duda': 'Widowed'}
        marital_status = marital_map.get(request.form.get('statusPernikahan', ''), '')
        
        # Customer data
        customer_data = {
            "id": customer_id,
            "customer_id": customer_id,
            "policy_id": request.form.get('nomorPolis', ''),
            "customer_no": request.form.get('nomorPeserta', ''),
            "card_no": request.form.get('nomorKartu', ''),
            "name": request.form.get('namaPeserta', '') if not request.form.get('isPemegangPolis') == 'true' else policy_holder_name,
            "dob": dob,
            "age": age,
            "gender": gender,
            "NIK": request.form.get('nik', ''),
            "phone": request.form.get('nomorTelepon', ''),
            "address": request.form.get('alamat', ''),
            "email": email,
            "password": password_hash,
            "is_policy_holder": request.form.get('isPemegangPolis') == 'true',
            "relation_with_policy_holder": "Self" if request.form.get('isPemegangPolis') == 'true' else request.form.get('hubungan', ''),
            "employment_status": "",
            "marital_status": marital_status,
            "income": None,
            "claim_id": [],
            "registration_docs": request.form.getlist('document_ids') or [],
            "insurance_company": request.form.get('perusahaanAsuransi', ''),
            "premium_plan": request.form.get('premiumPlan', '')
        }
        
        database.get_container_client("customer").create_item(customer_data)
        
        # Update documents with customer_id
        for doc_id in request.form.getlist('document_ids'):
            try:
                doc_data = cosmos_retrive_data(
                    "SELECT * FROM c WHERE c.doc_id = @docId",
                    "document",
                    [{"name": "@docId", "value": doc_id}]
                )
                if doc_data:
                    doc = doc_data[0]
                    doc['customer_id'] = customer_id
                    database.get_container_client("document").upsert_item(doc)
            except Exception as e:
                print(f"Error updating document {doc_id}: {e}")
        
        # Handle policy for non-policy holders
        is_policy_holder = request.form.get('isPemegangPolis') == 'true'
        
        if not is_policy_holder:
            existing_policy = cosmos_retrive_data(
                "SELECT * FROM c WHERE c.policy_id = @policyId",
                "policy",
                [{"name": "@policyId", "value": policy_id}]
            )
            
            if existing_policy:
                policy_record = existing_policy[0]
                if 'insured' not in policy_record:
                    policy_record['insured'] = []
                
                insured_info = {
                    "customer_id": customer_id,
                    "name": request.form.get('namaPeserta', ''),
                    "relation": request.form.get('hubungan', ''),
                    "added_date": datetime.now().isoformat()
                }
                policy_record['insured'].append(insured_info)
                database.get_container_client("policy").upsert_item(policy_record)
        
        # Session
        session['customer_id'] = customer_id
        session['email'] = email
        session['role'] = 'customer'
        session['name'] = customer_data['name']
        session['login_time'] = datetime.now().isoformat()
        session.permanent = False
        
        return jsonify({
            'status': 'success',
            'message': 'Customer registered successfully',
            'user': {
                'id': customer_id,
                'name': customer_data['name'],
                'email': email,
                'role': 'customer'
            },
            'documents_uploaded': len(request.form.getlist('document_ids'))
        })
        
    except Exception as e:
        print(f"Error in signup: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/signin', methods=['POST'])
def signin():
    data = request.json
    email = data.get('email', '')
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

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

    user_role = user.get('role', 'customer')
    
    session['customer_id'] = user['customer_id']
    session['email'] = email
    session['role'] = user_role
    session['name'] = user['name']
    session['login_time'] = datetime.now().isoformat()
    session.permanent = False
    
    return jsonify({
        'status': 'success',
        'message': 'Login successful',
        'user': {
            'id': user['customer_id'],
            'customer_id': user['customer_id'],
            'name': user['name'],
            'email': email,
            'role': user_role,
            'policy_id': user.get('policy_id', ''),
            'customer_no': user.get('customer_no', ''),
            'NIK': user.get('NIK', ''),
            'dob': user.get('dob', ''),
            'gender': user.get('gender', ''),
            'marital_status': user.get('marital_status', ''),
            'address': user.get('address', ''),
            'phone': user.get('phone', ''),
            'insurance_company': user.get('insurance_company', ''),
            'premium_plan': user.get('premium_plan', 'basic')
        }
    })

@app.route('/api/logout', methods=['POST'])
def logout():
    # Clear all session data
    session.clear()
    session.permanent = False
    
    # Create response
    response = jsonify({'status': 'success', 'message': 'Logged out successfully'})
    
    # Determine if we're in production
    is_production_env = os.getenv('FLASK_ENV') == 'production' or os.getenv('WEBSITE_HOSTNAME') is not None
    
    # Clear all possible session cookies with proper settings
    cookie_names = ['session', 'flask-session', 'idp_session', 'session_auth']
    
    for cookie_name in cookie_names:
        response.set_cookie(
            cookie_name, 
            '', 
            expires=0,
            max_age=0,
            path='/',
            domain=None,
            secure=is_production_env,
            httponly=True,
            samesite='None' if is_production_env else 'Lax'
        )
    
    # Add cache control headers to prevent caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    # Add CORS headers explicitly for logout
    origin = request.headers.get('Origin')
    if origin in allowed_origins or any(origin.endswith(allowed.replace('*', '')) for allowed in allowed_origins if '*' in allowed):
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    
    return response

@app.route('/api/session-status', methods=['GET'])
def session_status():
    # Check if session is expired first
    if check_session_expired():
        return jsonify({'status': 'not_authenticated'}), 401
    
    # Validate session data integrity
    required_fields = ['login_time', 'role']
    if not all(field in session for field in required_fields):
        session.clear()
        return jsonify({'status': 'not_authenticated'}), 401
    
    # Check if user ID exists
    if not (session.get('customer_id') or session.get('admin_id')):
        session.clear()
        return jsonify({'status': 'not_authenticated'}), 401
    
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

# =============================================================================
# MICROSOFT AUTH ROUTES
# =============================================================================
@app.route('/api/auth/microsoft', methods=['GET'])
def microsoft_auth():
    state = str(uuid.uuid4())
    session['oauth_state'] = state
    
    # Dynamic redirect URI based on request host
    if is_production:
        redirect_uri = 'https://idp-insurance.azurewebsites.net/api/auth/microsoft/callback'
    else:
        # Use the same host as the current request
        host = request.host
        redirect_uri = f"http://{host}/api/auth/microsoft/callback"
    
    # Store redirect URI in session for callback
    session['redirect_uri'] = redirect_uri
    
    params = {
        'client_id': AZURE_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'response_mode': 'query',
        'scope': 'openid profile email User.Read',
        'state': state
    }
    
    auth_url = f"{AUTHORIZE_URL}?{urlencode(params)}"
    return redirect(auth_url)

@app.route('/api/auth/microsoft/callback', methods=['GET'])
def microsoft_callback():
    try:
        print(f"Callback received with args: {request.args}")
        
        error = request.args.get('error')
        if error:
            error_desc = request.args.get('error_description', 'Unknown error')
            print(f"OAuth authentication failed: {error} - {error_desc}")
            return redirect(f'/signin?error={error}')
        
        state = request.args.get('state')
        stored_state = session.get('oauth_state')
        print(f"State comparison - received: {state}, stored: {stored_state}")
        
        if state != stored_state:
            print("State mismatch in OAuth callback")
            return redirect('/signin?error=invalid_state')
        
        code = request.args.get('code')
        if not code:
            print("No authorization code received")
            return redirect('/signin?error=no_code')
        
        # Get redirect URI from session
        redirect_uri = session.get('redirect_uri')
        if not redirect_uri:
            # Fallback to dynamic generation
            if is_production:
                redirect_uri = 'https://idp-insurance.azurewebsites.net/api/auth/microsoft/callback'
            else:
                host = request.host
                redirect_uri = f"http://{host}/api/auth/microsoft/callback"
        
        print(f"Requesting token with redirect_uri: {redirect_uri}")
        
        token_data = {
            'client_id': AZURE_CLIENT_ID,
            'client_secret': AZURE_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
            'scope': 'openid profile email User.Read'
        }
        
        token_response = requests.post(TOKEN_URL, data=token_data)
        print(f"Token response status: {token_response.status_code}")
        
        if token_response.status_code != 200:
            print(f"Token request failed: {token_response.text}")
            return redirect('/signin?error=token_request_failed')
            
        token_json = token_response.json()
        
        if 'access_token' not in token_json:
            print(f"No access token in response: {token_json}")
            return redirect('/signin?error=token_failed')
        
        headers = {'Authorization': f"Bearer {token_json['access_token']}"}
        user_response = requests.get(USER_INFO_URL, headers=headers)
        
        if user_response.status_code != 200:
            print(f"User info request failed: {user_response.status_code}")
            return redirect('/signin?error=user_info_failed')
            
        user_data = user_response.json()
        print(f"User data received: {user_data}")
        
        email = user_data.get('mail') or user_data.get('userPrincipalName')
        if not email:
            print("No email found in user data")
            return redirect('/signin?error=no_email')
        
        print(f"Looking for admin user with email: {email}")
        
        admin_user = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.email = @email",
            "insurance_admin",
            [{"name": "@email", "value": email}]
        )
        
        if not admin_user:
            print(f"Admin user not found for email: {email}")
            return redirect('/signin?error=user_not_found')
        
        admin = admin_user[0]
        print(f"Admin user found: {admin.get('name', 'Unknown')}")
        
        # Clear any existing session
        session.clear()
        
        # Set new session data
        session['customer_id'] = admin.get('admin_id', admin.get('id'))
        session['email'] = admin['email']
        session['role'] = 'approver'
        session['name'] = admin['name']
        session['admin_id'] = admin.get('admin_id', admin.get('id'))
        session['login_time'] = datetime.now().isoformat()
        session.permanent = True
        
        print(f"Session set for user: {admin['name']} with role: approver")
        
        # Create response with proper headers
        response = redirect('/approver-dashboard')
        
        # Set session cookie explicitly if needed
        if is_production:
            response.set_cookie('session_auth', 'true', 
                              secure=True, 
                              httponly=True, 
                              samesite='None',
                              max_age=3600)
        
        return response

    except Exception as e:
        print(f"Microsoft auth error: {e}")
        import traceback
        traceback.print_exc()
        return redirect('/signin?error=auth_failed')

# =============================================================================
# DOCUMENT ROUTES
# =============================================================================
@app.route('/api/extract-registration-info', methods=['POST'])
def extract_registration_info():
    try:
        extracted_data = {}
        uploaded_doc_ids = []
        
        if 'insurance_card' in request.files:
            file = request.files['insurance_card']
            if file.filename:
                doc_id = f"DOC{uuid.uuid4().hex[:8].upper()}"
                blob_name = f"registration/insurance_card/{doc_id}_{file.filename}"
                blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
                content_type = get_content_type(file)
                blob_client.upload_blob(file.read(), overwrite=True, content_settings=ContentSettings(content_type=content_type))
                
                insurance_data = analize_doc_registration(blob_name, "insuranceCard")
                if insurance_data and not insurance_data.get('error'):
                    extracted_data.update({
                        'policy_number': insurance_data.get('No. Polis', ''),
                        'participant_number': insurance_data.get('No. Peserta', ''),
                        'card_number': insurance_data.get('No. Kartu', '')
                    })
                
                doc_data = {
                    "id": doc_id,
                    "doc_id": doc_id,
                    "doc_type": "insurance_card",
                    "doc_blob_address": blob_name,
                    "upload_date": datetime.now().isoformat(),
                    "doc_contents": insurance_data or {}
                }
                database.get_container_client("document").create_item(doc_data)
                uploaded_doc_ids.append(doc_id)
        
        if 'id_card' in request.files:
            file = request.files['id_card']
            if file.filename:
                doc_id = f"DOC{uuid.uuid4().hex[:8].upper()}"
                blob_name = f"registration/id_card/{doc_id}_{file.filename}"
                blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
                content_type = get_content_type(file)
                blob_client.upload_blob(file.read(), overwrite=True, content_settings=ContentSettings(content_type=content_type))
                
                id_data = analize_doc_registration(blob_name, "idCard")
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
                
                doc_data = {
                    "id": doc_id,
                    "doc_id": doc_id,
                    "doc_type": "id_card",
                    "doc_blob_address": blob_name,
                    "upload_date": datetime.now().isoformat(),
                    "doc_contents": id_data or {}
                }
                database.get_container_client("document").create_item(doc_data)
                uploaded_doc_ids.append(doc_id)
        
        return jsonify({
            'status': 'success',
            'data': extracted_data,
            'document_ids': uploaded_doc_ids
        })
    
    except Exception as e:
        print(f"Error in document extraction: {e}")
        return jsonify({'error': 'Document processing failed'}), 500

@app.route('/api/documents/<doc_id>/download', methods=['GET'])
def download_document(doc_id):
    try:
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
        
        account_name = blob_service_client.account_name
        account_key = blob_service_client.credential.account_key
        
        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=container_name,
            blob_name=blob_address,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(minutes=15)
        )
        
        download_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_address}?{sas_token}"
        
        return jsonify({
            'status': 'success',
            'download_url': download_url,
            'filename': doc.get('doc_type', 'document') + '.pdf',
            'expires_in': 900
        })
        
    except Exception as e:
        print(f"Error generating download URL: {e}")
        return jsonify({'error': 'Failed to generate download URL'}), 500

@app.route('/api/documents/<doc_id>', methods=['GET'])
def get_document_metadata(doc_id):
    try:
        query = f"SELECT * FROM c WHERE c.doc_id = @docId"
        items = cosmos_retrive_data(query, "document",[{"name": "@docId", "value": doc_id}])
        if not items:
            return jsonify({"error": "Document not found"}), 404
        document = items[0]
        blob_path = document['doc_blob_address']
        document_url = get_sas_url(blob_path)
        document['doc_url'] = document_url
        return jsonify(document)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============================================================================
# CLAIM ROUTES
# =============================================================================
@app.route('/api/submit-claim', methods=['POST'])
def submit_claim():
    try:
        if 'customer_id' not in session or check_session_expired():
            return jsonify({'error': 'Authentication required'}), 401
        
        is_edit = request.form.get('isEdit') == 'true'
        existing_claim_id = request.form.get('claimId') if is_edit else None
        
        claim_type = request.form.get('claimType')
        claim_amount = request.form.get('claimAmount')
        currency = request.form.get('currency')
        customer_id = session['customer_id']
        policy_id = request.form.get('policyId')
        date_checkin = request.form.get('treatmentStartDate')
        date_checkout = request.form.get('treatmentEndDate')
        insurance_company = request.form.get('insuranceCompany')
        
        try:
            claim_amount_float = float(claim_amount) if claim_amount else 0
            if claim_amount_float <= 0:
                return jsonify({'error': 'Invalid claim amount'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid claim amount format'}), 400
        
        customer_data = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.customer_id = @customerId", 
            "customer", 
            [{"name": "@customerId", "value": customer_id}]
        )
        
        is_valid, message = validate_customer_data(request.form, customer_data)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        if is_edit:
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
                    is_valid, message = validate_file(file)
                    if not is_valid:
                        return jsonify({'error': f'{form_field}: {message}'}), 400
                    
                    doc_id = f"DOC{uuid.uuid4().hex[:8].upper()}"
                    blob_name = f"{blob_path}{doc_id}_{file.filename}"
                    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
                    content_type = get_content_type(file)
                    blob_client.upload_blob(file.read(), overwrite=True, content_settings=ContentSettings(content_type=content_type))
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
            "resubmitted": is_edit
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

@app.route('/api/analyze-claim', methods=['POST'])
def analyze_claim():
    try:
        data = request.json
        customer_id = data.get('customer_id')
        claim_id = data.get('claim_id')
        
        if not customer_id or not claim_id:
            return jsonify({'error': 'customer_id and claim_id required'}), 400
        
        run_analysis_async(customer_id, claim_id)
        
        return jsonify({'status': 'success', 'message': 'Analysis started'})
    
    except Exception as e:
        print(f"Error in analyze_claim: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/claims', methods=['GET'])
def get_all_claims():
    try:
        claims = list(database.get_container_client("claim").query_items(
            query="SELECT * FROM c",
            enable_cross_partition_query=True
        ))
        return claims
    except Exception as e:
        print(f"Error retrieving claims: {e}", file=sys.stderr)
        return []

@app.route('/api/claims/all-detailed', methods=['GET'])
def get_all_claims_detailed():
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
        
        if claim.get('claim_status') in ['Approved', 'Rejected'] and not claim.get('resubmitted'):
            return jsonify({'error': 'Claim already processed'}), 400
        
        claim['claim_status'] = status
        claim['admin_id'] = admin_id
        if notes == "":
            claim['admin_notes'] = claim["AI_reasoning"]
        else:
            claim['admin_notes'] = notes
        claim['processed_date'] = datetime.now().isoformat()
        claim['resubmitted'] = False
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

@app.route('/api/update-claim', methods=['POST'])
def update_claim():
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

# =============================================================================
# CUSTOMER ROUTES
# =============================================================================

@app.route('/api/customer/profile', methods=['GET'])
def get_customer_profile():
    try:
        if 'customer_id' not in session or check_session_expired():
            return jsonify({'error': 'Authentication required'}), 401
        
        customer_id = session['customer_id']
        customer_data = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.customer_id = @customerId",
            "customer",
            [{"name": "@customerId", "value": customer_id}]
        )
        print(customer_data)
        if not customer_data:
            return jsonify({'error': 'Customer not found'}), 404
        
        customer = customer_data[0]
        return jsonify({
            'status': 'success',
            'customer': customer
        })
        
    except Exception as e:
        print(f"Error getting customer profile: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/customer/<customer_id>/policy-limits', methods=['GET'])
def get_customer_policy_limits(customer_id):
    try:
        print(customer_id)  # Debugging line
        policy_data = cosmos_retrive_data(
            "SELECT c.total_claim_limit, c.policy_id FROM c WHERE ARRAY_CONTAINS(c.insured, {'customer_id': @CustomerId}, true) OR c.customer_id = @CustomerId",
            "policy",
            [{"name": "@CustomerId", "value": customer_id}]
        )
        print("policy_data:", policy_data)  # Debugging line
        if not policy_data:
            return jsonify({'status': 'error', 'message': 'Policy not found'}), 404

        policy = policy_data[0]
        policy_limit = float(policy['total_claim_limit'])
        policy_id = policy['policy_id']
        print("policy_id:", policy_id)  # Debugging line
        current_year = datetime.now().year
        claims_data = cosmos_retrive_data(
            "SELECT c.claim_amount FROM c WHERE c.policy_id = @PolicyId AND c.claim_status = 'Approved' AND CONTAINS(c.claim_date, @Year)",
            "claim",
            [{"name": "@PolicyId", "value": policy_id}, {"name": "@Year", "value": str(current_year)}]
        )
        print("claims_data:", claims_data)  # Debugging line
        total_used = sum(float(claim['claim_amount']) for claim in claims_data)
        print("total_used:", total_used)  # Debugging line
        return jsonify({
            'status': 'success',
            'policy_limit': policy_limit,
            'total_used': total_used,
            'current_year': current_year
        })

    except Exception as e:
        print(f"Error in get_customer_policy_limits: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@app.route('/api/customer/<customer_id>/policy', methods=['GET'])
def get_customer_policy(customer_id):
    try:
        print(customer_id)  # Debugging line
        policy_data = cosmos_retrive_data(
            "SELECT c.total_claim_limit, c.policy_id FROM c WHERE ARRAY_CONTAINS(c.insured, {'customer_id': @CustomerId}, true) OR c.customer_id = @CustomerId",
            "policy",
            [{"name": "@CustomerId", "value": customer_id}]
        )
        
        if not policy_data:
            return jsonify({'status': 'error', 'message': 'Policy not found'}), 404
        policy = policy_data[0]
        policy_limit = float(policy['total_claim_limit'])
        policy_id = policy['policy_id']
        current_year = datetime.now().year
        claims_data = cosmos_retrive_data(
            "SELECT c.claim_amount FROM c WHERE c.policy_id = @PolicyId AND c.claim_status = 'Approved' AND CONTAINS(c.claim_date, @Year)",
            "claim",
            [{"name": "@PolicyId", "value": policy_id}, {"name": "@Year", "value": str(current_year)}]
        )
        return jsonify({
            'status': 'success',
            'policy' : policy,
        })

    except Exception as e:
        print(f"Error in get_customer_policy_limits: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@app.route('/api/customer/<customer_id>/claims-detailed', methods=['GET'])
def get_customer_claims_detailed(customer_id):
    try:
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

@app.route('/api/customer-claim-history/<customer_id>', methods=['GET'])
def get_customer_claim_history(customer_id):
    try:
        if 'customer_id' not in session or check_session_expired():
            return jsonify({'error': 'Authentication required'}), 401
        
        user_role = session.get('role')
        if user_role != 'customer':
            return jsonify({'error': 'Access forbidden: Customers only'}), 403
        
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

# =============================================================================
# VALIDATION ROUTES
# =============================================================================
@app.route('/api/validate-participant', methods=['POST'])
def validate_participant():
    try:
        data = request.json
        participant_no = data.get('nomorPeserta')
        policy_id = data.get('nomorPolis')
        
        if not participant_no:
            return jsonify({'valid': True})
        
        existing_participant = cosmos_retrive_data(
            "SELECT * FROM c WHERE c.customer_no = @participantNo",
            "customer",
            [{"name": "@participantNo", "value": participant_no}]
        )
        
        if existing_participant:
            return jsonify({'valid': False, 'error': 'Participant number already exists', 'field': 'nomorPeserta'}), 400
        
        policy_holder_info = {}
        if policy_id:
            existing_policy_holder = cosmos_retrive_data(
                "SELECT * FROM c WHERE c.policy_id = @policyId AND c.is_policy_holder = true",
                "customer",
                [{"name": "@policyId", "value": policy_id}]
            )
            
            if existing_policy_holder:
                policy_holder = existing_policy_holder[0]
                policy_holder_info = {
                    'namaPemegang': policy_holder.get('name', ''),
                    'perusahaanAsuransi': policy_holder.get('insurance_company', ''),
                    'premiumPlan': policy_holder.get('premium_plan', '')
                }
        
        return jsonify({
            'valid': True,
            'policy_holder_info': policy_holder_info
        })
        
    except Exception as e:
        print(f"Error in validate_participant: {e}")
        return jsonify({'error': 'Validation failed'}), 500

# =============================================================================
# CHATBOT
# =============================================================================
@app.route('/api/chatbot', methods=['POST'])
def chatbot_api():
    try:
        data = request.json
        user_message = data.get('message')
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400

        user_message = str(user_message)    
        formatted_input = {
            "messages": [{"role": "user", "content": user_message}]
        }

        try:
            response = ''
            for chunk in agent.stream(input=formatted_input, config=config, stream_mode="values"):
                response = chunk
            response = response['messages'][-1].content  
            response = str(response)
            return jsonify({'response': response})
        except Exception as agent_error:
            print(f"Agent error: {agent_error}")
            return jsonify({'response': 'Maaf, chatbot sedang mengalami gangguan. Silakan coba lagi nanti.'}), 500

    except Exception as e:
        print(f"Error in chatbot: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

# =============================================================================
# APPLICATION STARTUP
# =============================================================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = '127.0.0.1' if os.environ.get('FLASK_ENV') == 'development' else '0.0.0.0'
    app.run(debug=True, host=host, port=port)
