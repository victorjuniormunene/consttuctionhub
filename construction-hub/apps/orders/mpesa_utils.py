import requests
import json
import base64
from datetime import datetime
from django.conf import settings
from django.core.mail import send_mail
from .models import Order


class MpesaService:
    """M-Pesa API integration service"""

    def __init__(self):
        self.config = settings.MPESA_CONFIG
        self.base_url = self.config['BASE_URL']
        self.consumer_key = self.config['CONSUMER_KEY']
        self.consumer_secret = self.config['CONSUMER_SECRET']
        self.business_shortcode = self.config['BUSINESS_SHORTCODE']
        self.passkey = self.config['PASSKEY']
        self.account_reference = self.config['ACCOUNT_REFERENCE']
        self.transaction_desc = self.config['TRANSACTION_DESC']
        self.callback_url = self.config['CALLBACK_URL']

    def get_access_token(self):
        """Get M-Pesa access token"""
        try:
            # Encode consumer key and secret
            credentials = base64.b64encode(
                f"{self.consumer_key}:{self.consumer_secret}".encode()
            ).decode()

            headers = {
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/json'
            }

            response = requests.get(
                f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials",
                headers=headers
            )

            if response.status_code == 200:
                return response.json()['access_token']
            else:
                print(f"Failed to get access token: {response.text}")
                return None
        except Exception as e:
            print(f"Error getting access token: {str(e)}")
            return None

    def generate_password(self):
        """Generate password for STK push"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_str = f"{self.business_shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_str.encode()).decode()
        return password, timestamp

    def initiate_stk_push(self, phone_number, amount, order_number, account_reference=None, callback_url=None):
        """Initiate STK push for payment"""
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {'success': False, 'error': 'Failed to get access token'}

            # Format phone number (remove + and ensure it starts with 254)
            phone_number = phone_number.replace('+', '')
            if phone_number.startswith('0'):
                phone_number = '254' + phone_number[1:]
            elif not phone_number.startswith('254'):
                phone_number = '254' + phone_number

            password, timestamp = self.generate_password()

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            # Use custom callback_url if provided, otherwise use default
            final_callback_url = callback_url if callback_url else self.callback_url

            payload = {
                'BusinessShortCode': self.business_shortcode,
                'Password': password,
                'Timestamp': timestamp,
                'TransactionType': 'CustomerPayBillOnline',
                'Amount': int(amount),
                'PartyA': phone_number,
                'PartyB': self.business_shortcode,
                'PhoneNumber': phone_number,
                'CallBackURL': final_callback_url,
                'AccountReference': account_reference or self.account_reference,
                'TransactionDesc': f"{self.transaction_desc} - {order_number}"
            }

            print(f"Initiating STK push for phone: {phone_number}, amount: {amount}")
            print(f"Payload: {payload}")

            response = requests.post(
                f"{self.base_url}/mpesa/stkpush/v1/processrequest",
                json=payload,
                headers=headers
            )

            print(f"STK Push Response Status: {response.status_code}")
            print(f"STK Push Response: {response.text}")

            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'checkout_request_id': result.get('CheckoutRequestID'),
                    'response_code': result.get('ResponseCode'),
                    'response_description': result.get('ResponseDescription'),
                    'customer_message': result.get('CustomerMessage')
                }
            else:
                error_msg = f"STK push failed: {response.status_code} - {response.text}"
                print(error_msg)
                return {
                    'success': False,
                    'error': error_msg
                }
        except Exception as e:
            error_msg = f"Exception during STK push: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': error_msg
            }

    def process_callback(self, callback_data):
        """Process M-Pesa callback"""
        try:
            # Extract callback data
            stk_callback = callback_data.get('Body', {}).get('stkCallback', {})

            if stk_callback.get('ResultCode') == 0:
                # Payment successful
                callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])

                transaction_id = None
                phone_number = None

                for item in callback_metadata:
                    if item.get('Name') == 'MpesaReceiptNumber':
                        transaction_id = item.get('Value')
                    elif item.get('Name') == 'PhoneNumber':
                        phone_number = item.get('Value')

                checkout_request_id = stk_callback.get('CheckoutRequestID')

                # Update order status - handle both single and bulk payments
                try:
                    # Get all orders with this checkout_request_id (handles bulk payments)
                    orders = Order.objects.filter(mpesa_checkout_request_id=checkout_request_id)

                    if not orders.exists():
                        return {'success': False, 'message': 'Order not found'}

                    updated_orders = []
                    for order in orders:
                        order.payment_status = 'completed'
                        order.mpesa_transaction_id = transaction_id
                        order.mpesa_phone_number = phone_number
                        order.status = 'paid'  # Changed from 'completed' to 'paid' to match manual update
                        order.payment_completed_at = datetime.now()
                        order.save()
                        updated_orders.append(order)

                        # Send email notification to supplier for each order
                        try:
                            mpesa_service.send_payment_notification_email(order)
                        except Exception as e:
                            print(f"Failed to send payment notification email for order {order.order_number}: {str(e)}")
                            # Don't fail the payment processing if email fails

                        # Send email notification to customer (like manual update does)
                        try:
                            from .views import send_payment_confirmation_email_to_customer
                            send_payment_confirmation_email_to_customer(order)
                        except Exception as e:
                            print(f"Failed to send payment confirmation email to customer for order {order.order_number}: {str(e)}")

                        # Send SMS notification to customer (like manual update does)
                        try:
                            from .sms_utils import send_payment_confirmation_sms
                            send_payment_confirmation_sms(order)
                        except Exception as e:
                            print(f"Failed to send payment confirmation SMS for order {order.order_number}: {str(e)}")

                    return {'success': True, 'message': f'Payment processed successfully for {len(updated_orders)} order(s)'}
                except Exception as e:
                    return {'success': False, 'message': f'Error updating orders: {str(e)}'}
            else:
                # Payment failed
                checkout_request_id = stk_callback.get('CheckoutRequestID')
                try:
                    order = Order.objects.get(mpesa_checkout_request_id=checkout_request_id)
                    order.payment_status = 'failed'
                    order.save()
                except Order.DoesNotExist:
                    pass

                return {
                    'success': False,
                    'message': f"Payment failed: {stk_callback.get('ResultDesc', 'Unknown error')}"
                }
        except Exception as e:
            return {'success': False, 'message': f"Callback processing error: {str(e)}"}

    def send_payment_notification_email(self, order):
        """Send email notification to supplier when payment is completed"""
        try:
            if not order.product or not order.product.supplier:
                print(f"No supplier found for order {order.order_number}")
                return

            supplier = order.product.supplier
            customer = order.customer

            subject = f"Payment Received - Order #{order.order_number} Paid"

            message = f"""
Dear {supplier.company_name},

Great news! Payment has been successfully received for Order #{order.order_number}.

Order Details:
- Order Number: {order.order_number}
- Product: {order.product.name}
- Quantity: {order.quantity}
- Unit Price: KSH {order.price}
- Total Amount: KSH {order.total_cost}
- Payment Transaction ID: {order.mpesa_transaction_id}

Customer Information:
- Name: {customer.get_full_name() if customer.get_full_name() else customer.username}
- Phone: {order.customer_number}
- Location: {order.customer_location}

Payment was completed on: {order.payment_completed_at.strftime('%Y-%m-%d %H:%M:%S') if order.payment_completed_at else 'N/A'}

You can now proceed with fulfilling this order. Please ensure timely delivery to maintain customer satisfaction.

Best regards,
Construction Hub Team
"""

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[supplier.user.email],
                fail_silently=False,
            )

            print(f"Payment notification email sent to supplier {supplier.company_name} for order {order.order_number}")

        except Exception as e:
            print(f"Error sending payment notification email: {str(e)}")
            raise


# Global instance
mpesa_service = MpesaService()


def initiate_mpesa_payment(order, phone_number):
    """Helper function to initiate M-Pesa payment for an order"""
    amount = order.total_cost

    result = mpesa_service.initiate_stk_push(
        phone_number=phone_number,
        amount=amount,
        order_number=order.order_number,
        account_reference=f"Order-{order.order_number}"
    )

    if result.get('success'):
        # Update order with payment details
        order.mpesa_checkout_request_id = result['checkout_request_id']
        order.mpesa_phone_number = phone_number
        order.status = 'pending_payment'
        order.payment_status = 'pending'
        order.payment_initiated_at = datetime.now()
        order.save()

    return result


def initiate_bulk_mpesa_payment(orders, phone_number):
    """Helper function to initiate M-Pesa payment for multiple orders"""
    if not orders:
        return {'success': False, 'error': 'No orders provided'}

    total_amount = sum(order.total_cost for order in orders)

    # Use the first order's order_number as reference for the bulk payment
    bulk_reference = orders[0].order_number if orders else "Bulk-Order"

    result = mpesa_service.initiate_stk_push(
        phone_number=phone_number,
        amount=total_amount,
        order_number=bulk_reference,
        account_reference=f"Order-{bulk_reference}"
    )

    if result.get('success'):
        # Update all orders with the payment details
        for order in orders:
            order.mpesa_checkout_request_id = result['checkout_request_id']
            order.mpesa_phone_number = phone_number
            order.status = 'pending_payment'
            order.payment_status = 'pending'
            order.payment_initiated_at = datetime.now()
            order.save()

    return result


def initiate_mpesa_payment_for_amount(amount, phone_number, reference, callback_url=None):
    """Helper function to initiate M-Pesa payment for a specific amount"""
    result = mpesa_service.initiate_stk_push(
        phone_number=phone_number,
        amount=amount,
        order_number=reference,
        account_reference=reference,
        callback_url=callback_url
    )

    return result


def initiate_consultation_payment(consultation, phone_number):
    """Helper function to initiate M-Pesa payment for a consultation booking"""
    from django.conf import settings
    
    amount = float(consultation.consultation_rate)
    reference = f"CONSULT-{consultation.id}"
    
    # Use consultation-specific callback URL if available, otherwise use default
    callback_url = getattr(settings, 'MPESA_CONSULTATION_CALLBACK_URL', None)
    
    result = mpesa_service.initiate_stk_push(
        phone_number=phone_number,
        amount=amount,
        order_number=reference,
        account_reference=reference,
        callback_url=callback_url
    )

    return result
