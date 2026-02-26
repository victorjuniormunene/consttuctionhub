"""
Direct test script for Beem Africa SMS API
"""
import os
import sys
import base64
import json
import requests
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'construction_hub'))
django.setup()

from django.conf import settings

def test_beem_sms():
    # Get credentials
    api_key = getattr(settings, 'BEEM_AFRICA_API_KEY', '')
    secret_key = getattr(settings, 'BEEM_AFRICA_SECRET_KEY', '')
    sender_id = getattr(settings, 'BEEM_AFRICA_SENDER_ID', '')
    
    print(f"API Key: {api_key}")
    print(f"Sender ID: {sender_id}")
    
    # Format phone number
   254790199098 phone = "+"
    clean_phone = phone.replace(' ', '').replace('-', '').replace('+', '')
    if clean_phone.startswith('0'):
        clean_phone = '254' + clean_phone[1:]
    if not clean_phone.startswith('254'):
        clean_phone = '254' + clean_phone
    
    print(f"Formatted phone: {clean_phone}")
    
    # Prepare request
    url = 'https://apisms.beem.africa/v1/send'
    auth_string = f'{api_key}:{secret_key}'
    auth_header = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {auth_header}'
    }
    
    data = {
        'source_addr': sender_id,
        'schedule_time': '',
        'encoding': 0,
        'message': 'Test message from Construction Hub',
        'recipients': [
            {'recipient_id': 1, 'dest_addr': clean_phone}
        ]
    }
    
    print(f"\nRequest URL: {url}")
    print(f"Request data: {json.dumps(data, indent=2)}")
    print(f"Auth header: {auth_header[:30]}...")
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        print(f"\nStatus code: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code in [200, 201]:
            print("\n✓ SMS sent successfully!")
            return True
        else:
            print(f"\n✗ SMS sending failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_beem_sms()
