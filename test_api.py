#!/usr/bin/env python3
"""Quick test script to verify PP-StructureV3 API connection"""

import requests
import base64
import os
import sys

API_URL = "https://wfk3ide9lcd0x0k9.aistudio-app.com/layout-parsing"
TOKEN = "031c87b3c44d16aa4adf6928bcfa132e23393afc"

def test_api_with_sample():
    """Test API with a minimal sample (1x1 white PNG)"""
    
    # Create a minimal test image (1x1 white pixel PNG)
    # This is a valid 1x1 white PNG in base64
    test_image_b64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    )
    
    headers = {
        "Authorization": f"token {TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "file": test_image_b64,
        "fileType": 1,  # Image
        "useTableRecognition": True
    }
    
    print(f"Testing API: {API_URL}")
    print(f"Token: {TOKEN[:10]}...{TOKEN[-10:]}")
    print("\nSending request...")
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")
        print(f"\nResponse body (first 500 chars):")
        print(response.text[:500])
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("\n✅ API call successful!")
                print(f"Result keys: {list(result.keys())}")
                return True
            except Exception as e:
                print(f"\n❌ Got 200 but couldn't parse JSON: {e}")
                return False
        else:
            print(f"\n❌ API returned error status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_api_with_sample()
    sys.exit(0 if success else 1)
