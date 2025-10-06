from doc_intel_for_registration import analize_doc

# Test insurance card processing
print("=== Testing Insurance Card Processing ===")
insurance_result = analize_doc("registration/REGE7AE92AA_insurance%20card.jpg", "insuranceCard")
print("Insurance card extraction result:", insurance_result)

print("\n=== Testing ID Card Processing ===")
# Test ID card processing using the actual blob path
id_result = analize_doc("registration/REGDADF01F8_cara-mudah-cek-ktp-asli-atau-palsu.jpeg", "idCard")
print("ID card extraction result:", id_result)