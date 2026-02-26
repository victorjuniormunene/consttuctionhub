"""
SMS Utility Module for Construction Hub
Uses Beem Africa SMS API to send SMS notifications to customers
"""

import logging
import base64
import json
import re
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def get_beem_credentials():
    """Get Beem Africa credentials from settings"""
    api_key = getattr(settings, 'BEEM_AFRICA_API_KEY', '')
    secret_key = getattr(settings, 'BEEM_AFRICA_SECRET_KEY', '')
    # If BEEM_AFRICA_SENDER_ID is not set, allow Beem to use its numeric default sender
    raw_sender = getattr(settings, 'BEEM_AFRICA_SENDER_ID', None)
    sender_id = None
    use_sender = False
    if raw_sender:
        sanitized = re.sub(r'[^A-Za-z0-9]', '', str(raw_sender))[:11]
        if sanitized:
            sender_id = sanitized
            # mark that we will include sender only if explicitly provided in settings
            use_sender = True
    base_url = getattr(settings, 'BEEM_AFRICA_BASE_URL', 'https://apisms.beem.africa')
    
    return {
        'api_key': api_key,
        'secret_key': secret_key,
        'sender_id': sender_id,
        'use_sender': use_sender,
        'base_url': base_url
    }


def is_beem_configured():
    """Check if Beem Africa is properly configured"""
    creds = get_beem_credentials()
    return bool(creds['api_key'] and creds['secret_key'])


def format_phone_number(phone_number):
    """
    Format phone number to international format without +
    Example: +254712731468 -> 254712731468, 0712731468 -> 254712731468
    
    Args:
        phone_number: The recipient's phone number (e.g., '+254712345678' or '0712345678')
    
    Returns:
        str: Formatted phone number without + (e.g., '254712731468')
    """
    if not phone_number:
        return None
    
    # Remove any spaces or dashes
    clean_phone = phone_number.replace(' ', '').replace('-', '').replace('+', '')
    
    # If it starts with '0', replace with '254' (Kenya country code)
    if clean_phone.startswith('0'):
        clean_phone = '254' + clean_phone[1:]
    
    # If it doesn't start with '254', add '254'
    if not clean_phone.startswith('254'):
        clean_phone = '254' + clean_phone
    
    return clean_phone


def send_sms(phone_number, message):
    """
    Send an SMS to a phone number using Beem Africa API
    
    Args:
        phone_number: The recipient's phone number (e.g., '+254712345678' or '0712345678')
        message: The message content to send
    
    Returns:
        dict: Response containing 'success' boolean and 'message' or 'error' details
    """
    # Validate phone number
    if not phone_number:
        return {'success': False, 'error': 'Phone number is required'}
    
    # Get Beem Africa credentials
    creds = get_beem_credentials()
    
    # Check if credentials are configured
    if not is_beem_configured():
        error_msg = "Beem Africa API credentials not configured. Please set BEEM_AFRICA_API_KEY and BEEM_AFRICA_SECRET_KEY in settings."
        logger.error(error_msg)
        return {'success': False, 'error': error_msg}
    
    # Format phone number to international format without +
    formatted_phone = format_phone_number(phone_number)
    
    if not formatted_phone:
        return {'success': False, 'error': 'Invalid phone number format'}
    
    try:
        # Prepare the request
        url = f"{creds['base_url']}/v1/send"
        
        # Create Basic Auth header (Base64 encoded API_KEY:SECRET_KEY)
        auth_string = f"{creds['api_key']}:{creds['secret_key']}"
        auth_header = base64.b64encode(auth_string.encode()).decode()
        
        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {auth_header}'
        }
        
        # Prepare body - do NOT include source_addr so Beem can assign numeric sender
        data = {
            "schedule_time": "",
            "encoding": 0,
            "message": str(message),
            "recipients": [
                {
                    "recipient_id": 1,
                    "dest_addr": str(formatted_phone)
                }
            ]
        }

        # Mask sensitive headers for logging
        masked_headers = dict(headers)
        if 'Authorization' in masked_headers:
            masked_headers['Authorization'] = 'REDACTED'

        logger.info(f"Sending SMS to {formatted_phone} via Beem Africa (no source_addr)")
        logger.debug(f"Request URL: {url}")
        logger.debug(f"Request headers: {masked_headers}")
        try:
            logger.debug(f"Request body: {json.dumps(data)[:2000]}")
        except Exception:
            logger.debug("Request body: <unserializable>")
        
        logger.info(f"Sending SMS to {formatted_phone} via Beem Africa")
        logger.debug(f"Request URL: {url}")
        logger.debug(f"Request data: {json.dumps(data)}")
        
        # Send the request using json parameter which properly serializes the data
        response = requests.post(url, json=data, headers=headers, timeout=30)

        # Safely parse JSON response (some error responses may not be JSON)
        try:
            response_data = response.json()
        except ValueError:
            response_data = {'raw_text': response.text}
            logger.error("Beem Africa returned non-JSON response", extra={
                'status_code': response.status_code,
                'text': response.text[:1000]
            })

        logger.info(f"Beem Africa response status: {response.status_code}")
        logger.debug(f"Beem Africa response body: {response_data}")

        # Consider common success indicators across different Beem responses
        status_ok = response.status_code in (200, 201, 202)
        resp_success_flag = False
        if isinstance(response_data, dict):
            if response_data.get('successful'):
                resp_success_flag = True
            if response_data.get('success'):
                resp_success_flag = True
            code = response_data.get('code')
            if code == 100:
                resp_success_flag = True
            status_field = response_data.get('status')
            if status_field and str(status_field).lower() in ('success', 'successful'):
                resp_success_flag = True

        if status_ok and resp_success_flag:
            return {
                'success': True,
                'message': response_data.get('message', 'SMS sent successfully'),
                'request_id': response_data.get('request_id'),
                'response': response_data,
                'status_code': response.status_code
            }

        # If we reach here it's a failure - check for specific sender-id error and retry without sender
        error_msg = None
        if isinstance(response_data, dict):
            error_msg = response_data.get('message') or response_data.get('error') or response_data.get('raw_text')
        else:
            error_msg = getattr(response, 'text', None)

        error_msg = error_msg or f'HTTP Error: {response.status_code}'
        # If invalid sender id, retry without source_addr so Beem assigns a numeric sender
        try_retry_without_sender = False
        if isinstance(response_data, dict):
            # Beem sometimes nests error details under a 'data' key
            nested = response_data.get('data') if isinstance(response_data.get('data'), dict) else response_data
            code = nested.get('code')
            msg = str(nested.get('message') or '').lower()
            if code == 111 or 'invalid sender' in msg or 'invalid sender id' in msg:
                try_retry_without_sender = True

        if try_retry_without_sender:
            logger.warning('Invalid Sender Id detected - retrying send without source_addr')
            # Ensure retry request also omits source_addr
            data_no_sender = dict(data)
            data_no_sender.pop('source_addr', None)
            logger.debug(f"Retry request headers: {masked_headers}")
            try:
                logger.debug(f"Retry request body: {json.dumps(data_no_sender)[:2000]}")
            except Exception:
                logger.debug("Retry request body: <unserializable>")
            try:
                response2 = requests.post(url, json=data_no_sender, headers=headers, timeout=30)
                try:
                    response2_data = response2.json()
                except ValueError:
                    response2_data = {'raw_text': response2.text}

                logger.info(f"Beem Africa retry response status: {response2.status_code}")
                logger.debug(f"Beem Africa retry response body: {response2_data}")

                if response2.status_code in (200, 201, 202):
                    # consider same success indicators
                    resp_success = False
                    if isinstance(response2_data, dict):
                        if response2_data.get('successful') or response2_data.get('success'):
                            resp_success = True
                        if response2_data.get('code') == 100:
                            resp_success = True
                    if resp_success:
                        return {
                            'success': True,
                            'message': response2_data.get('message', 'SMS sent successfully (numeric sender)'),
                            'request_id': response2_data.get('request_id'),
                            'response': response2_data,
                            'status_code': response2.status_code,
                            'note': 'sent_without_sender'
                        }

                # If retry failed, return its result for debugging
                err = None
                if isinstance(response2_data, dict):
                    err = response2_data.get('message') or response2_data.get('error') or response2_data.get('raw_text')
                else:
                    err = getattr(response2, 'text', None)
                err = err or f'HTTP Error: {response2.status_code}'
                logger.error(f"Beem Africa retry error: {err}")
                return {'success': False, 'error': err, 'status_code': response2.status_code, 'response': response2_data}
            except Exception as e:
                logger.error(f"Retry without sender failed: {e}")
                return {'success': False, 'error': str(e)}

        logger.error(f"Beem Africa API error: {error_msg}")
        return {
            'success': False,
            'error': error_msg,
            'status_code': response.status_code,
            'response': response_data
        }
        
    except requests.exceptions.Timeout:
        error_msg = "Request to Beem Africa API timed out"
        logger.error(error_msg)
        return {'success': False, 'error': error_msg}
    except requests.exceptions.RequestException as e:
        error_msg = f"Request error: {str(e)}"
        logger.error(error_msg)
        return {'success': False, 'error': error_msg}
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return {'success': False, 'error': error_msg}


def check_delivery_status(phone_number, request_id):
    """
    Check the delivery status of an SMS using Beem Africa API
    
    Args:
        phone_number: The recipient's phone number
        request_id: The request ID returned when sending the SMS
    
    Returns:
        dict: Response containing delivery status or error
    """
    if not phone_number or not request_id:
        return {'success': False, 'error': 'Phone number and request ID are required'}
    
    creds = get_beem_credentials()
    
    if not is_beem_configured():
        error_msg = "Beem Africa API credentials not configured"
        logger.error(error_msg)
        return {'success': False, 'error': error_msg}
    
    try:
        # Format phone number
        formatted_phone = format_phone_number(phone_number)
        
        # Prepare request
        url = f"{creds['base_url']}/public/v1/delivery-reports"
        params = {
            'dest_addr': formatted_phone,
            'request_id': request_id
        }
        
        # Create Basic Auth header
        auth_string = f"{creds['api_key']}:{creds['secret_key']}"
        auth_header = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {auth_header}'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return {
                'success': True,
                'data': response.json()
            }
        else:
            return {
                'success': False,
                'error': f'HTTP Error: {response.status_code}'
            }
            
    except Exception as e:
        logger.error(f"Error checking delivery status: {str(e)}")
        return {'success': False, 'error': str(e)}


def send_payment_confirmation_sms(order):
    """
    Send payment confirmation SMS to customer when payment is successful
    
    Args:
        order: The Order object that has been paid
    
    Returns:
        dict: Response containing 'success' boolean and 'message' or 'error' details
    """
    try:
        # Get customer's phone number - prioritize different sources
        phone_number = None
        
        # Try to get from order's mpesa_phone_number (most reliable for payment)
        if order.mpesa_phone_number:
            phone_number = order.mpesa_phone_number
        # Try to get from order's customer_number
        elif order.customer_number:
            phone_number = order.customer_number
        # Try to get from customer user profile
        elif order.customer and hasattr(order.customer, 'phone_number') and order.customer.phone_number:
            phone_number = order.customer.phone_number
        
        if not phone_number:
            logger.warning(f"No phone number found for order {order.order_number}")
            return {'success': False, 'error': 'No phone number found for customer'}
        
        # Build the message
        customer_name = order.customer.get_full_name() if order.customer else order.customer_name or 'Customer'
        product_name = order.product.name if order.product else (f"Plan: {order.plan_type}" if order.plan_type else 'your order')
        
        message = f"""Dear {customer_name},

Great news! Your payment of KSH {order.total_cost} for Order #{order.order_number} has been successfully received.

Order Details:
- Product: {product_name}
- Amount: KSH {order.total_cost}
- Transaction ID: {order.mpesa_transaction_id or 'N/A'}

Your order will be delivered within 24 hours. Thank you for choosing Construction Hub!

Best regards,
Construction Hub Team"""
        
        # Send the SMS
        result = send_sms(phone_number, message)
        
        if result.get('success'):
            logger.info(f"Payment confirmation SMS sent for order {order.order_number}")
            return result

        # SMS failed - fall back to email notification
        logger.warning(f"SMS failed for order {order.order_number} ({result.get('error')}). Falling back to email.")
        try:
            from django.core.mail import send_mail
            from django.conf import settings as dj_settings

            recipient = None
            if order.customer and getattr(order.customer, 'email', None):
                recipient = order.customer.email

            # If we don't have customer email, try to use order.customer_number as a proxy (not an email)
            if not recipient:
                logger.error(f"No customer email available for order {order.order_number}; cannot send fallback email")
                return {'success': False, 'error': result.get('error'), 'sms_response': result}

            subject = f"Payment confirmed for Order #{order.order_number}"
            email_message = message

            send_mail(
                subject=subject,
                message=email_message,
                from_email=getattr(dj_settings, 'DEFAULT_FROM_EMAIL', None),
                recipient_list=[recipient],
                fail_silently=False,
            )

            logger.info(f"Fallback email sent to {recipient} for order {order.order_number}")
            return {'success': True, 'message': 'SMS failed; email sent as fallback', 'sms_response': result}
        except Exception as e:
            logger.error(f"Failed to send fallback email for order {order.order_number}: {e}")
            return {'success': False, 'error': result.get('error'), 'sms_response': result, 'email_error': str(e)}
        
    except Exception as e:
        logger.error(f"Error sending payment confirmation SMS: {str(e)}")
        return {'success': False, 'error': str(e)}
