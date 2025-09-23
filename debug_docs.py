import sys
sys.path.append('endpoint')
from analyst_tools import get_all_claims_with_documents

try:
    claims = get_all_claims_with_documents()
    print(f'Number of claims: {len(claims)}')
    
    for i, claim in enumerate(claims[:3]):  # Just check first 3 claims
        print(f'\nClaim {i+1}: {claim.get("id", "no-id")}')
        if 'document_details' in claim:
            print(f'  Document details count: {len(claim["document_details"])}')
            for j, doc in enumerate(claim['document_details']):
                name = doc.get('name', 'no-name')
                doc_id = doc.get('id', 'no-id')
                print(f'    Doc {j+1}: name="{name}" id={doc_id}')
        else:
            print('  No document_details found')
            if 'documents' in claim:
                print(f'  Documents array: {claim["documents"]}')

except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()