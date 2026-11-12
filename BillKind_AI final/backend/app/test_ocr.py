import urllib.request
import json

boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
with open(r'C:\Users\Dell\Downloads\trainticket.pdf', 'rb') as f:
    pdf_bytes = f.read()

part_header = f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="trainticket.pdf"\r\nContent-Type: application/pdf\r\n\r\n'.encode('utf-8')
part_footer = f'\r\n--{boundary}--\r\n'.encode('utf-8')
body = part_header + pdf_bytes + part_footer

req = urllib.request.Request(
    'http://localhost:8000/api/v1/bills/upload-and-ocr',
    data=body,
    headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
)

with urllib.request.urlopen(req) as res:
    resp = json.loads(res.read().decode('utf-8'))
    print('OCR Upload Response Success:', resp.get('success'))
    print('Clean Filename:', resp.get('clean_filename'))
    print('File URL:', resp.get('file_url'))
    print('Extracted Data:', json.dumps(resp.get('extracted'), indent=2))
