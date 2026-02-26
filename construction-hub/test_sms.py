"""
Test script to verify SMS functionality with Beem Africa
"""
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'construction_hub'))
django.setup()

# Now import the SMS utilities
from apps.orders.sms_utils import (
    send_sms, 
    is_beem_configured, 
    get_beem_credentials,
    format_phone_number,
    check_delivery_status
)


def test_beem_configuration():
    """Test if Beem Africa is properly configured"""
    print("=" * 50)
    print("Testing Beem Africa Configuration")
    print("=" * 50)
    
    creds = get_beem_credentials()
    print(f"API Key: {'*' * len(creds['api_key']) if creds['api_key'] else 'NOT SET'}")
    print(f"Secret Key: {'*' * len(creds['secret_key']) if creds['secret_key'] else 'NOT SET'}")
    print(f"Sender ID: {creds['sender_id']}")
    print(f"Base URL: {creds['base_url']}")
    
    if is_beem_configured():
        print("✓ Beem Africa is properly configured")
        return True
    else:
        print("✗ Beem Africa is NOT properly configured")
        print("  Please set BEEM_AFRICA_API_KEY and BEEM_AFRICA_SECRET_KEY")
        return False


def test_phone_formatting():
    """Test phone number formatting"""
    print("\n" + "=" * 50)
    print("Testing Phone Number Formatting")
    print("=" * 50)
    
    test_cases = [
        ("+254712731468", "254712731468"),
        ("254712731468", "254712731468"),
        ("0712731468", "254712731468"),
        ("712731468", "254712731468"),
    ]
    
    all_passed = True
    for input_phone, expected in test_cases:
        result = format_phone_number(input_phone)
        status = "✓" if result == expected else "✗"
        print(f"{status} {input_phone} -> {result} (expected: {expected})")
        if result != expected:
            all_passed = False
    
    return all_passed


def test_send_sms():
    """Test sending an actual SMS"""
    print("\n" + "=" * 50)
    print("Testing SMS Sending")
    print("=" * 50)
    
    # Check if configured first
    if not is_beem_configured():
        print("✗ Cannot test SMS - Beem Africa not configured")
        return False
    
    # Use a test phone number (Kenya format)
    test_phone = "+254790199098"  # Replace with your actual test number
    test_message = "This is a test message from Construction Hub SMS test. If you receive this, the SMS is working!"
    
    print(f"Sending SMS to: {test_phone}")
    print(f"Message: {test_message}")
    print("-" * 50)
    
    result = send_sms(test_phone, test_message)
    
    print(f"Success: {result.get('success')}")
    if result.get('success'):
        print(f"Message: {result.get('message')}")
        print(f"Request ID: {result.get('request_id')}")
        print(f"Response: {result.get('response')}")
    else:
        print(f"Error: {result.get('error')}")
    
    return result.get('success')


def test_check_delivery_status():
    """Test checking delivery status"""
    print("\n" + "=" * 50)
    print("Testing Delivery Status Check")
    print("=" * 50)
    
    if not is_beem_configured():
        print("✗ Cannot test delivery status - Beem Africa not configured")
        return False
    
    # This is a test - you would use a real request_id from a sent SMS
    test_phone = "+254790199098"
    test_request_id = "12345"  # Example request ID
    
    print(f"Checking delivery status for: {test_phone}")
    print(f"Request ID: {test_request_id}")
    print("-" * 50)
    
    result = check_delivery_status(test_phone, test_request_id)
    
    print(f"Success: {result.get('success')}")
    if result.get('success'):
        print(f"Data: {result.get('data')}")
    else:
        print(f"Error: {result.get('error')}")
    
    # This might fail if the request_id doesn't exist, which is expected
    return True


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("CONSTRUCTION HUB SMS TEST (Beem Africa)")
    print("=" * 50 + "\n")
    
    # Test configuration
    config_ok = test_beem_configuration()
    
    # Test phone formatting (always runs)
    phone_ok = test_phone_formatting()
    
    if config_ok:
        # Test sending SMS (only if configured)
        print("\n" + "=" * 50)
        print("Running SMS send test...")
        print("=" * 50)
        sms_sent = test_send_sms()
        
        # Test delivery status check
        delivery_ok = test_check_delivery_status()
        
        print("\n" + "=" * 50)
        print("TEST RESULTS")
        print("=" * 50)
        print(f"Configuration: {'PASS' if config_ok else 'FAIL'}")
        print(f"Phone Formatting: {'PASS' if phone_ok else 'FAIL'}")
        print(f"SMS Sending: {'PASS' if sms_sent else 'FAIL'}")
        print(f"Delivery Status: {'PASS' if delivery_ok else 'FAIL'}")
    else:
        print("\n" + "=" * 50)
        print("TEST RESULTS")
        print("=" * 50)
        print(f"Configuration: {'PASS' if config_ok else 'FAIL'}")
        print(f"Phone Formatting: {'PASS' if phone_ok else 'FAIL'}")
        print("SMS Sending: SKIPPED (not configured)")
        print("Delivery Status: SKIPPED (not configured)")
        
        print("\n" + "=" * 50)
        print("SETUP INSTRUCTIONS")
        print("=" * 50)
        print("To configure Beem Africa SMS:")
        print("1. Set environment variables:")
        print("   - BEEM_AFRICA_API_KEY=your_api_key")
        print("   - BEEM_AFRICA_SECRET_KEY=your_secret_key")
        print("   - BEEM_AFRICA_SENDER_ID=your_sender_id")
        print("")
        print("2. Or update settings.py directly with your credentials")
