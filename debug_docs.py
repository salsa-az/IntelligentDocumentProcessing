import sys
import os
sys.path.append('endpoint')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the functions directly from app.py instead of making HTTP requests
try:
    from endpoint.app import safe_fetch_documents, safe_fetch_customer
    from endpoint.analyst_tools import cosmos_retrive_data
    from dotenv import load_dotenv
    load_dotenv()
    
    DIRECT_FUNCTION_CALL = True
except ImportError as e:
    print(f"Warning: Could not import app functions: {e}")
    import requests
    import json
    BASE_URL = 'http://localhost:5000'
    DIRECT_FUNCTION_CALL = False

def test_all_claims_detailed():
    """Test claims with documents using direct function calls or API"""
    try:
        if DIRECT_FUNCTION_CALL:
            print("Testing claims retrieval using direct function calls...")
            
            # Get all claims directly from database
            claims = cosmos_retrive_data(
                "SELECT * FROM c ORDER BY c._ts DESC", 
                "claim", 
                []
            )
            
            if not claims:
                print("❌ No claims found in database")
                return
                
            print(f'✅ Direct DB Query Success')
            print(f'📊 Number of claims: {len(claims)}')
            
            # Process first 3 claims
            for i, claim in enumerate(claims[:3]):
                print(f'\n📋 Claim {i+1}: {claim.get("claim_id", "no-id")}')
                print(f'   Customer ID: {claim.get("customer_id", "no-customer")}')
                print(f'   Status: {claim.get("claim_status", "no-status")}')
                print(f'   Documents in claim: {claim.get("documents", [])}')
                
                # Test document fetching
                document_details = safe_fetch_documents(claim.get('documents', []))
                print(f'   📄 Document details fetched: {len(document_details)}')
                
                for j, doc in enumerate(document_details):
                    doc_id = doc.get('doc_id', 'no-id')
                    doc_type = doc.get('doc_type', 'no-type')
                    has_contents = 'doc_contents' in doc and doc['doc_contents']
                    
                    print(f'      Doc {j+1}: id={doc_id}, type={doc_type}, has_contents={has_contents}')
                    
                    # Show doc_contents structure if available
                    if has_contents:
                        contents = doc['doc_contents']
                        if isinstance(contents, dict):
                            keys = list(contents.keys())
                            print(f'         📝 Content keys ({len(keys)}): {keys[:5]}{"..." if len(keys) > 5 else ""}')
                            
                            # Show sample content for each key
                            for key in keys[:3]:
                                value = contents[key]
                                if isinstance(value, dict):
                                    print(f'            {key}: dict with {len(value)} fields')
                                elif isinstance(value, str):
                                    preview = value[:50] + "..." if len(value) > 50 else value
                                    print(f'            {key}: "{preview}"')
                                else:
                                    print(f'            {key}: {type(value)} - {value}')
                        else:
                            print(f'         📝 Content type: {type(contents)} - {str(contents)[:100]}')
                    else:
                        print(f'         ❌ No doc_contents found')
                        print(f'         📝 Available fields: {list(doc.keys())}')
        else:
            # Fallback to API call
            print("Testing /api/claims/all-detailed endpoint...")
            response = requests.get(f'{BASE_URL}/api/claims/all-detailed')
            
            if response.status_code == 200:
                data = response.json()
                claims = data.get('claims', [])
                print(f'✅ API Response Status: {data.get("status")}')
                print(f'📊 Number of claims: {len(claims)}')
                
                for i, claim in enumerate(claims[:3]):  # Just check first 3 claims
                    print(f'\n📋 Claim {i+1}: {claim.get("claim_id", "no-id")}')
                    print(f'   Customer ID: {claim.get("customer_id", "no-customer")}')
                    print(f'   Status: {claim.get("claim_status", "no-status")}')
                    
                    if 'document_details' in claim:
                        docs = claim['document_details']
                        print(f'   📄 Document details count: {len(docs)}')
                        for j, doc in enumerate(docs):
                            doc_id = doc.get('doc_id', 'no-id')
                            doc_type = doc.get('doc_type', 'no-type')
                            has_contents = 'doc_contents' in doc and doc['doc_contents']
                            print(f'      Doc {j+1}: id={doc_id}, type={doc_type}, has_contents={has_contents}')
                            
                            # Show doc_contents structure if available
                            if has_contents:
                                contents = doc['doc_contents']
                                if isinstance(contents, dict):
                                    print(f'         📝 Content keys: {list(contents.keys())[:5]}...')
                                else:
                                    print(f'         📝 Content type: {type(contents)}')
                    else:
                        print('   ❌ No document_details found')
                        if 'documents' in claim:
                            print(f'   📎 Raw documents array: {claim["documents"]}')
            else:
                print(f'❌ API Error: {response.status_code} - {response.text}')
            
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

def test_specific_document():
    """Test fetching a specific document to check doc_contents"""
    try:
        if DIRECT_FUNCTION_CALL:
            print("\n🔍 Testing specific document retrieval...")
            
            # Get all documents to see what's available
            all_docs = cosmos_retrive_data(
                "SELECT * FROM c", 
                "document", 
                []
            )
            
            print(f'📄 Total documents in database: {len(all_docs)}')
            
            if all_docs:
                # Check first few documents
                for i, doc in enumerate(all_docs[:3]):
                    doc_id = doc.get('doc_id', 'no-id')
                    doc_type = doc.get('doc_type', 'no-type')
                    has_contents = 'doc_contents' in doc
                    
                    print(f'\n   📋 Document {i+1}: id={doc_id}, type={doc_type}')
                    print(f'      Fields: {list(doc.keys())}')
                    print(f'      Has doc_contents: {has_contents}')
                    
                    if has_contents:
                        contents = doc['doc_contents']
                        if contents:
                            if isinstance(contents, dict):
                                print(f'      Content structure: {list(contents.keys())}')
                            else:
                                print(f'      Content type: {type(contents)}')
                        else:
                            print(f'      doc_contents is empty: {contents}')
                    
                    # Check if document has been processed
                    if 'processed_date' in doc:
                        print(f'      Processed: {doc["processed_date"]}')
                    else:
                        print(f'      Not processed yet')
            else:
                print('❌ No documents found in database')
        
    except Exception as e:
        print(f'❌ Document test error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting API Debug Tests...")
    print("=" * 50)
    
    test_all_claims_detailed()
    test_specific_document()
    
    print("\n" + "=" * 50)
    print("✨ Debug tests completed!")