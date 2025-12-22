import json
with open(r'd:\als_knowledgebase\als_compass_web_application\git_project_als_compass\als-compass\data\als_comprehensive_faq.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    if 'categories' in data:
        for cat in data['categories']:
            print(f"ID: {cat.get('id')} | Name: {cat.get('name')}")
    else:
        print("No 'categories' key found")
