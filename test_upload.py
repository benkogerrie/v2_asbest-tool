
import requests
import os

# Upload the PDF
pdf_path = r"C:\Users\meteo\asbest authoratisatie\fouten deel 3\fouten deel 3\24.7779 Nieuwe Holleweg 61 Beek-Ubbergen.pdf"
url = "https://v2asbest-tool-production.up.railway.app/reports/"

with open(pdf_path, 'rb') as f:
    files = {'file': (os.path.basename(pdf_path), f, 'application/pdf')}
    
    # Note: This requires authentication
    response = requests.post(url, files=files)
    print(f"Upload Status: {response.status_code}")
    print(f"Response: {response.text}")
