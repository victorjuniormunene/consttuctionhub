#!/usr/bin/env python
"""
Script to manually fix order payment status for ORD-00000380
"""
import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from apps.orders.models import Order
from apps.orders.mpesa_utils import mpesa_service

def fix_order_payment():
    try:
        # Get the order
        order = Order.objects.get(order_number='ORD-00000380')

        print(f"Current order status: {order.status}")
        print(f"Current payment status: {order.payment_status}")
        print(f"Current transaction ID: {order.mpesa_transaction_id}")

        # Update the order with payment details
        order.status = 'paid'
        order.payment_status = 'completed'
        order.mpesa_transaction_id = 'UBB7G6CK90'
        order.payment_completed_at = datetime.now()

        # Save the order
        order.save()

        print("Order updated successfully!")
        print(f"New order status: {order.status}")
        print(f"New payment status: {order.payment_status}")
        print(f"New transaction ID: {order.mpesa_transaction_id}")

        # Send notification email to supplier
        try:
            mpesa_service.send_payment_notification_email(order)
            print("Payment notification email sent to supplier.")
        except Exception as e:
            print(f"Failed to send notification email: {str(e)}")

        # Reduce product quantity if applicable
        if order.product and order.status == 'paid':
            order.product.available_quantity -= order.quantity
            order.product.save()
            print(f"Product quantity reduced. New available quantity: {order.product.available_quantity}")

        return True

    except Order.DoesNotExist:
        print("Order ORD-00000380 not found!")
        return False
    except Exception as e:
        print(f"Error updating order: {str(e)}")
        return False

if __name__ == '__main__':
    success = fix_order_payment()
    if success:
        print("Order payment fix completed successfully!")
    else:
        print("Failed to fix order payment.")
        sys.exit(1)
