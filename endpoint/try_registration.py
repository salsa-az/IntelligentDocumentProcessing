from doc_intel_for_registration import analize_doc

# # Test insurance card processing (mock data)
# print("=== Testing Insurance Card Processing ===")
# insurance_result = analize_doc("test_insurance_card.jpg", "insurance card")
# print("Insurance card result:", insurance_result)

print("\n=== Testing ID Card Processing ===")
# Test ID card processing using the actual blob path
id_result = analize_doc("registration/REGDADF01F8_cara-mudah-cek-ktp-asli-atau-palsu.jpeg", "id card")
print("ID card result:", id_result)