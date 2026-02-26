#!/usr/bin/env python
"""
Test script to verify M-Pesa API credentials
"""
import requests
import base64
from django.conf import settings

def test_mpesa_access_token():
    """Test M-Pesa access token generation"""
    try:
        # Get credentials from settings
        consumer_key = settings.MPESA_CONFIG['CONSUMER_KEY']
        consumer_secret = settings.MPESA_CONFIG['CONSUMER_SECRET']
        base_url = settings.MPESA_CONFIG['BASE_URL']

        print(f"Testing M-Pesa credentials...")
        print(f"Consumer Key: {consumer_key[:10]}...")
        print(f"Consumer Secret: {consumer_secret[:10]}...")
        print(f"Base URL: {base_url}")

        # Encode consumer key and secret
        credentials = base64.b64encode(
            f"{consumer_key}:{consumer_secret}".encode()
        ).decode()

        headers = {
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/json'
        }

        url = f"{base_url}/oauth/v1/generate"
        querystring = {"grant_type": "client_credentials"}

        print(f"Making request to: {url}")

        response = requests.get(url, headers=headers, params=querystring)

        print(f"Response Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            access_token = result.get('access_token')
            print("✅ SUCCESS: Access token obtained!")
            print(f"Access Token: {access_token[:20]}...")
            print(f"Expires In: {result.get('expires_in')} seconds")
            return True
        else:
            print("❌ FAILED: Could not get access token")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    import os
    import django

    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
    django.setup()

    # Test the credentials
    success = test_mpesa_access_token()

    if success:
        print("\n🎉 M-Pesa credentials are working correctly!")
    else:
        print("\n💥 M-Pesa credentials test failed. Please check your credentials.")
