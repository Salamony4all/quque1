#!/usr/bin/env python3
"""Test API with actual PDF file"""

import requests
import base64
import os
import sys

API_URL = "https://wfk3ide9lcd0x0k9.aistudio-app.com/layout-parsing"
TOKEN = "031c87b3c44d16aa4adf6928bcfa132e23393afc"

def test_with_pdf(pdf_path):
    """Test API with an actual PDF file"""
    
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return False
    
    file_size = os.path.getsize(pdf_path)
    print(f"Testing with PDF: {pdf_path}")
    print(f"File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
    
    with open(pdf_path, 'rb') as f:
        file_bytes = f.read()
        file_data = base64.b64encode(file_bytes).decode('ascii')
    
    print(f"Base64 encoded size: {len(file_data):,} chars")
    
    headers = {
        "Authorization": f"token {TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "file": file_data,
        "fileType": 0,  # PDF
        "useTableRecognition": True,
        "useTextlineOrientation": True,
        "useDocOrientationClassify": True,
        "visualize": True
    }
    
    print(f"\nSending request to: {API_URL}")
    print("This may take 30-60 seconds for PDF processing...\n")
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=120)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("\n✅ API call successful!")
                print(f"Response keys: {list(result.keys())}")
                
                if 'result' in result:
                    res = result['result']
                    print(f"Result keys: {list(res.keys())}")
                    
                    if 'layoutParsingResults' in res:
                        print(f"Pages processed: {len(res['layoutParsingResults'])}")
                        
                        for i, page_res in enumerate(res['layoutParsingResults']):
                            print(f"\nPage {i+1}:")
                            if 'markdown' in page_res and 'text' in page_res['markdown']:
                                md_text = page_res['markdown']['text']
                                print(f"  Markdown length: {len(md_text)} chars")
                                print(f"  Preview: {md_text[:200]}...")
                
                return True
            except Exception as e:
                print(f"\n❌ Got 200 but couldn't parse JSON: {e}")
                print(f"Response preview: {response.text[:500]}")
                return False
        else:
            print(f"\n❌ API returned error status: {response.status_code}")
            print(f"Response: {response.text[:1000]}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n❌ Request timed out (>120s)")
        return False
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    pdf_path = "/workspaces/quque1/uploads/48fb7ec3-ddff-434c-81a0-aa7ff34b5840/9db72e65-01d7-45ca-adad-e18765301768_RAKHYUT.pdf"
    success = test_with_pdf(pdf_path)
    sys.exit(0 if success else 1)
