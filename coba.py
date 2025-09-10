import json 
with open("hasil_analisis.json", 'r') as f:
        data = json.load(f)
def ekstrak_semua_field(extraction_raw):
    # Pastikan ada dokumen yang dianalisis
    if not extraction_raw.get('documents'):
        print("Tidak ada dokumen yang ditemukan dalam hasil analisis.")
        return
    invoice = extraction_raw['documents'][0]
    for field_name, field_data in invoice.get('fields', {}).items():
        if field_name == 'Items':
            continue
        value = field_data.get(f"value{field_data.get('type').capitalize()}", field_data.get('content'))
        hasil_ekstraksi = value
        field_content = field_data.get('content', 'N/A')
    items_field = invoice.get('fields', {}).get('Items')
    if items_field and items_field.get('type') == 'array':
        for i, item_row in enumerate(items_field.get('valueArray', [])):
            if item_row.get('type') == 'object':
                for item_field_name, item_field_data in item_row.get('valueObject', {}).items():
                    item_content = item_field_data.get('content', 'N/A')
            if item_dict: # Hanya tambahkan jika dictionary item tidak kosong
                items_list.append(item_dict)
        
        # Tambahkan list item ke dictionary hasil utama
        hasil_ekstraksi = items_list