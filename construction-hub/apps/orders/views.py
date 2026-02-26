from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from ..orders.models import Order
from ..orders.forms import OrderForm
from ..products.models import Product
from ..consultations.pdf_utils import generate_order_receipt_pdf_customer

@login_required
def order_detail(request, order_id):
    """Display order details for the customer"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    context = {
        'order': order,
    }
    
    return render(request, 'orders/order_detail.html', context)


@login_required
def order_list(request):
    """List all orders for the current user"""
    from apps.messaging.models import Conversation
    
    # Get orders where user is the customer
    orders = Order.objects.filter(
        customer=request.user
    ).select_related('product__supplier__user').order_by('-created_at')
    
    # Add supplier info to each order for messaging
    for order in orders:
        # Get or create supplier information
        if order.product and hasattr(order.product, 'supplier'):
            order.has_supplier = True
            order.supplier_name = order.product.supplier.company_name or order.product.supplier.user.username
            # Get unread count for conversation with supplier
            try:
                conversation = Conversation.objects.filter(
                    order=order,
                    customer=request.user,
                    supplier=order.product.supplier.user
                ).first()
                order.supplier_unread_count = conversation.unread_count if conversation else 0
            except:
                order.supplier_unread_count = 0
        else:
            order.has_supplier = False
            order.supplier_name = None
            order.supplier_unread_count = 0
    
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def payment(request, order_id):
    """Handle payment for an order"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)

    # Check if order is already paid
    if order.status == 'paid':
        messages.info(request, 'This order has already been paid.')
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        if not phone_number:
            messages.error(request, 'Please provide your M-Pesa phone number.')
            return redirect('orders:payment', order_id=order.id)

        # Initiate M-Pesa STK push
        from .mpesa_utils import initiate_mpesa_payment
        result = initiate_mpesa_payment(order, phone_number)

        if result.get('success'):
            messages.success(request, f'M-Pesa payment initiated! Please check your phone and enter your PIN to complete the payment. Order #{order.order_number}')
            return redirect('accounts:dashboard')
        else:
            messages.error(request, f'Failed to initiate payment: {result.get("error", "Unknown error")}')
            return redirect('orders:payment', order_id=order.id)

    # Payment number for M-Pesa (this should come from settings)
    payment_number = getattr(settings, 'MPESA_PAYBILL_NUMBER', '123456')

    return render(request, 'orders/payment.html', {
        'order': order,
        'payment_number': payment_number,
    })

@login_required
def edit_supplier_order(request, order_id):
    """Edit an order for a supplier's product"""
    order = get_object_or_404(Order, id=order_id)

    # Check if user is the supplier for this order
    is_supplier = order.product.supplier.user == request.user if order.product and order.product.supplier else False

    if not is_supplier:
        messages.error(request, 'You do not have permission to edit this order.')
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f'Order #{order.order_number} updated successfully!')
            return redirect('dashboard:supplier_dashboard')
    else:
        form = OrderForm(instance=order)

    return render(request, 'orders/order_edit_supplier.html', {
        'order': order,
        'form': form
    })

@login_required
def delete_supplier_order(request, order_id):
    """Delete an order for a supplier's product"""
    order = get_object_or_404(Order, id=order_id)

    # Check if user is the supplier for this order
    is_supplier = order.product.supplier.user == request.user if order.product and order.product.supplier else False

    if not is_supplier:
        messages.error(request, 'You do not have permission to delete this order.')
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        order_number = order.order_number
        order.delete()
        messages.success(request, f'Order #{order_number} deleted successfully!')
        return redirect('dashboard:supplier_dashboard')

    # If not POST, redirect back
    return redirect('dashboard:supplier_dashboard')

@login_required
def order_create(request):
    """Create an order for a product"""
    if not getattr(request.user, 'user_type', None) == 'customer':
        messages.error(request, 'Only customers can create orders.')
        return redirect('accounts:dashboard')

    product_id = request.GET.get('product')
    if not product_id:
        messages.error(request, 'Product not specified.')
        return redirect('products:product_list')

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        messages.error(request, 'Product not found.')
        return redirect('products:product_list')

    if request.method == 'POST':
        form = OrderForm(request.POST, product=product)
        if form.is_valid():
            order = form.save(commit=False)
            order.product = product
            order.customer = request.user
            order.status = 'pending_payment'
            # Automatically apply the product's offer if it has one
            if product.offer:
                order.offer = product.offer
            order.save()
            messages.success(request, f'Order #{order.order_number} created successfully! Total: KSH {order.total_cost}')
            return redirect('orders:payment', order_id=order.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    else:
        form = OrderForm(product=product)

    return render(request, 'orders/order_form.html', {
        'form': form,
        'product': product,
    })

@login_required
def manual_mpesa_update(request):
    """Allow customers to manually update order status by pasting M-Pesa message"""
    if request.method == 'POST':
        mpesa_message = request.POST.get('mpesa_message', '').strip()

        if not mpesa_message:
            messages.error(request, 'Please paste the M-Pesa confirmation message.')
            return redirect('dashboard:customer_dashboard')

        # Parse M-Pesa message
        # Example payment: "UBB7G6CRBZ Confirmed. KSH10.00 sent to Daraja-Sandbox for account Order-ORD-00000387 on 11/2/26 at 4:12 PM New M-PESA balance is KSH0.37. Transaction cost, KSH0.00.Amount you can transact within the day is 499,980.00. Save frequent paybills for quick payment on M-PESA app https://bit.ly/mpesalnk"
        # Example reversal: "UBB7GI2065 confirmed. Reversal of transaction UBB7G6CRBZ has been successfully reversed on 11/2/26 at 5:00 PM and Ksh10.00 is credited to your M-PESA account. New M-PESA account balance is Ksh10.37."

        import re
        from datetime import datetime

        # Check if this is a reversal message
        if re.search(r'Reversal of transaction', mpesa_message, re.IGNORECASE):
            # Handle reversal
            reversal_match = re.search(r'Reversal of transaction\s+([A-Z0-9]+)', mpesa_message, re.IGNORECASE)
            if not reversal_match:
                messages.error(request, 'Invalid reversal message format. Could not find original transaction ID.')
                return redirect('dashboard:customer_dashboard')

            original_transaction_id = reversal_match.group(1)

            # Find the order with this original transaction ID
            try:
                order = Order.objects.get(mpesa_transaction_id=original_transaction_id)
            except Order.DoesNotExist:
                messages.error(request, f'No order found with transaction ID {original_transaction_id}.')
                return redirect('dashboard:customer_dashboard')
            except Order.MultipleObjectsReturned:
                messages.error(request, f'Multiple orders found with transaction ID {original_transaction_id}. Please contact support.')
                return redirect('dashboard:customer_dashboard')

            # Update order status to cancelled (payment was reversed)
            order.status = 'canceled'
            order.payment_status = 'failed'
            order.save()

            # Restore product quantity if it was reduced during payment
            if order.product and order.status == 'paid':
                order.product.available_quantity += order.quantity
                order.product.save()

            messages.success(request, f'Order #{order.order_number} payment was reversed. Order status updated to cancelled.')
            return redirect('dashboard:customer_dashboard')

        # Handle normal payment confirmation
        # Extract transaction ID (first part before "Confirmed")
        transaction_id_match = re.search(r'([A-Z0-9]{6,})\s+Confirmed', mpesa_message, re.IGNORECASE)
        if not transaction_id_match:
            messages.error(request, f'Invalid M-Pesa message format. Could not find transaction ID. Message: {mpesa_message[:100]}...')
            return redirect('dashboard:customer_dashboard')

        transaction_id = transaction_id_match.group(1)

        # Extract account reference (after "for account")
        account_match = re.search(r'for account\s+([^\s]+)', mpesa_message)
        if not account_match:
            messages.error(request, 'Invalid M-Pesa message format. Could not find account reference.')
            return redirect('dashboard:customer_dashboard')

        account_reference = account_match.group(1)

        # Get phone number from form input (new feature - user can now enter their phone number)
        # This takes priority over extracting from M-Pesa message
        phone_number = request.POST.get('phone_number', '').strip() if request.POST.get('phone_number') else None
        
        # If no phone from form, try to extract from M-Pesa message
        if not phone_number:
            phone_match = re.search(r'(?:for account\s+[^\s]+\s+on\s+\d+/\d+/\d+\s+at\s+\d+:\d+\s*[AP]M\s*)?(\+?254[1-9]\d{8})', mpesa_message, re.IGNORECASE)
            if phone_match:
                phone_number = phone_match.group(1)
                # Clean up the phone number
                phone_number = phone_number.replace('+', '').replace(' ', '').replace('-', '')
                if not phone_number.startswith('254'):
                    phone_number = '254' + phone_number
        
        # Also try to get phone from order's customer user profile as fallback
        customer_phone = None
        if hasattr(request.user, 'phone_number') and request.user.phone_number:
            customer_phone = request.user.phone_number

        # Extract order number from account reference (format: Order-ORD-XXXXXXXXX)
        order_number_match = re.search(r'Order-(ORD-\d+)', account_reference)
        if not order_number_match:
            messages.error(request, 'Invalid account reference format. Expected format: Order-ORD-XXXXXXXXX')
            return redirect('dashboard:customer_dashboard')

        order_number = order_number_match.group(1)

        # Find the order(s) for this customer - handle both single and bulk payments
        try:
            # First try to find the specific order
            order = Order.objects.get(
                order_number=order_number,
                customer=request.user,
                status__in=['pending_payment', 'saved']  # Only allow updating pending orders
            )

            # Check if this is part of a bulk payment (multiple orders with same checkout_request_id)
            if order.mpesa_checkout_request_id:
                # Get all orders with the same checkout_request_id (bulk payment)
                bulk_orders = Order.objects.filter(
                    mpesa_checkout_request_id=order.mpesa_checkout_request_id,
                    customer=request.user,
                    status__in=['pending_payment', 'saved']
                )
                if bulk_orders.count() > 1:
                    # This is a bulk payment - update all orders
                    updated_orders = []
                    for bulk_order in bulk_orders:
                        if bulk_order.status != 'paid':  # Skip already paid orders
                            bulk_order.payment_status = 'completed'
                            bulk_order.mpesa_transaction_id = transaction_id
                            bulk_order.status = 'paid'
                            bulk_order.payment_completed_at = datetime.now()
                            bulk_order.save()
                            updated_orders.append(bulk_order)

                            # Send email notification to supplier
                            try:
                                from .mpesa_utils import mpesa_service
                                mpesa_service.send_payment_notification_email(bulk_order)
                            except Exception as e:
                                print(f"Failed to send payment notification email for order {bulk_order.order_number}: {str(e)}")

                            # Send email notification to customer
                            try:
                                send_payment_confirmation_email_to_customer(bulk_order)
                            except Exception as e:
                                print(f"Failed to send payment confirmation email to customer for order {bulk_order.order_number}: {str(e)}")

                            # Send SMS notification to customer
                            try:
                                from .sms_utils import send_payment_confirmation_sms
                                send_payment_confirmation_sms(bulk_order)
                            except Exception as e:
                                print(f"Failed to send payment confirmation SMS for order {bulk_order.order_number}: {str(e)}")

                    if updated_orders:
                        order_numbers = [o.order_number for o in updated_orders]
                        messages.success(request, f'Orders {", ".join(order_numbers)} status updated successfully! Payment confirmed for {len(updated_orders)} items.')
                        return redirect('dashboard:customer_dashboard')

            # Single order payment
            # Check if order is already paid
            if order.status == 'paid':
                messages.info(request, f'Order #{order.order_number} is already marked as paid.')
                return redirect('dashboard:customer_dashboard')

            # Determine the phone number to save - use M-Pesa message phone if available, otherwise use customer phone
            final_phone = phone_number if phone_number else customer_phone
            
            # Update order status
            order.payment_status = 'completed'
            order.mpesa_transaction_id = transaction_id
            order.status = 'paid'
            order.payment_completed_at = datetime.now()
            # Save the phone number if we have one
            if final_phone:
                order.mpesa_phone_number = final_phone
            order.save()

            # Send email notification to supplier
            try:
                from .mpesa_utils import mpesa_service
                mpesa_service.send_payment_notification_email(order)
            except Exception as e:
                print(f"Failed to send payment notification email: {str(e)}")

            # Send email notification to customer
            try:
                send_payment_confirmation_email_to_customer(order)
            except Exception as e:
                print(f"Failed to send payment confirmation email to customer for order {order.order_number}: {str(e)}")

            # Send SMS notification to customer
            sms_result = None
            try:
                from .sms_utils import send_payment_confirmation_sms
                sms_result = send_payment_confirmation_sms(order)
                if sms_result and sms_result.get('success'):
                    messages.success(request, f'Order #{order.order_number} status updated successfully! Payment confirmed. You will receive an SMS shortly.')
                else:
                    sms_error = sms_result.get('error', 'Unknown error') if sms_result else 'SMS service unavailable'
                    messages.warning(request, f'Order #{order.order_number} status updated successfully! Payment confirmed. Note: SMS could not be sent ({sms_error}). Please check your email for confirmation.')
            except Exception as e:
                print(f"Failed to send payment confirmation SMS for order {order.order_number}: {str(e)}")
                messages.warning(request, f'Order #{order.order_number} status updated successfully! Payment confirmed. Note: SMS notification could not be sent. Please check your email for confirmation.')

            return redirect('dashboard:customer_dashboard')

        except Order.DoesNotExist:
            messages.error(request, f'No pending order found with order number {order_number}.')
            return redirect('dashboard:customer_dashboard')
        except Order.MultipleObjectsReturned:
            messages.error(request, f'Multiple orders found with order number {order_number}. Please contact support.')
            return redirect('dashboard:customer_dashboard')

    # If GET request, redirect back
    return redirect('dashboard:customer_dashboard')

def send_order_created_email_with_offer(order):
    """Send email notification to customer when an order is created with an offer applied"""
    try:
        customer = order.customer
        
        # Get offer details
        offer_text = ""
        if order.offer == '10_percent_discount':
            offer_text = "10% Discount Applied!"
            # Calculate discount amount
            from decimal import Decimal
            original_total = order.price * order.quantity
            discount = original_total * Decimal('0.10')
            offer_text += f"\nYou saved: KSH {discount}"
        elif order.offer == 'free_delivery':
            offer_text = "Free Delivery Applied!"
        
        subject = f"Order Created - #{order.order_number} - Offer Applied!"
        
        if offer_text:
            message = f"""
Dear {customer.get_full_name() or customer.username},

Great news! Your order has been created successfully with a special offer!

Order Details:
- Order Number: {order.order_number}
- Product: {order.product.name if order.product else 'N/A'}
- Quantity: {order.quantity}
- Unit Price: KSH {order.price}
- Applied Offer: {offer_text}
- Total Amount: KSH {order.total_cost}

Your order is now pending payment. Please complete your payment to confirm the order.

If you have any questions, please contact our support team.

Best regards,
Construction Hub Team
"""
        else:
            message = f"""
Dear {customer.get_full_name() or customer.username},

Your order has been created successfully!

Order Details:
- Order Number: {order.order_number}
- Product: {order.product.name if order.product else 'N/A'}
- Quantity: {order.quantity}
- Unit Price: KSH {order.price}
- Total Amount: KSH {order.total_cost}

Your order is now pending payment. Please complete your payment to confirm the order.

If you have any questions, please contact our support team.

Best regards,
Construction Hub Team
"""

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[customer.email],
            fail_silently=False,
        )

        print(f"Order creation email with offer info sent to customer {customer.username} for order {order.order_number}")

    except Exception as e:
        print(f"Error sending order creation email to customer: {str(e)}")


def send_payment_confirmation_email_to_customer(order):
    """Send email notification to customer when payment is completed"""
    try:
        customer = order.customer

        subject = f"Payment Confirmed - Order #{order.order_number} Paid Successfully"

        message = f"""
Dear {customer.get_full_name() or customer.username},

Great news! Your payment has been successfully processed for Order #{order.order_number}.

Order Details:
- Order Number: {order.order_number}
- Product: {order.product.name if order.product else 'N/A'}
- Quantity: {order.quantity}
- Unit Price: KSH {order.price}
- Total Amount: KSH {order.total_cost}
- Payment Transaction ID: {order.mpesa_transaction_id}

Payment was completed on: {order.payment_completed_at.strftime('%Y-%m-%d %H:%M:%S') if order.payment_completed_at else 'N/A'}

Your order is now marked as 'Paid' and will be processed by the supplier. You will receive updates on the order status.

If you have any questions, please contact our support team.

Best regards,
Construction Hub Team
"""

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[customer.email],
            fail_silently=False,
        )

        print(f"Payment confirmation email sent to customer {customer.username} for order {order.order_number}")

    except Exception as e:
        print(f"Error sending payment confirmation email to customer: {str(e)}")
        raise


def send_order_completion_email_to_customer(order):
    """Send email notification to customer when order is marked as completed by supplier"""
    try:
        customer = order.customer

        subject = f"Order Completed - Order #{order.order_number} Has Been Delivered"

        message = f"""
Dear {customer.get_full_name() or customer.username},

Great news! Your order #{order.order_number} has been completed and delivered by the supplier.

Order Details:
- Order Number: {order.order_number}
- Product: {order.product.name if order.product else 'N/A'}
- Quantity: {order.quantity}
- Unit Price: KSH {order.price}
- Total Amount: KSH {order.total_cost}
- Payment Transaction ID: {order.mpesa_transaction_id}

The supplier has confirmed that your order has been fulfilled and is now complete. If you have any feedback or need further assistance, please don't hesitate to contact us.

Thank you for choosing Construction Hub!

Best regards,
Construction Hub Team
"""

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[customer.email],
            fail_silently=False,
        )

        print(f"Order completion email sent to customer {customer.username} for order {order.order_number}")

    except Exception as e:
        print(f"Error sending order completion email to customer: {str(e)}")
        raise


@login_required
def download_receipt(request, order_id):
    """Download PDF receipt for an order"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)

    # Check if order is paid
    if order.status != 'paid':
        messages.error(request, 'Receipt is only available for paid orders.')
        return redirect('accounts:dashboard')

    # Generate PDF receipt
    pdf_buffer = generate_order_receipt_pdf_customer(order)

    # Create response
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{order.order_number}.pdf"'
    return response


@csrf_exempt
def mpesa_callback(request):
    """Handle M-Pesa callback"""
    if request.method == 'POST':
        import json
        import logging
        logger = logging.getLogger(__name__)
        callback_data = json.loads(request.body.decode('utf-8'))

        logger.info(f"M-Pesa callback received: {callback_data}")

        # Process the callback
        from .mpesa_utils import mpesa_service
        result = mpesa_service.process_callback(callback_data)

        logger.info(f"Callback processing result: {result}")

        if result.get('success'):
            return JsonResponse({'success': True, 'message': result.get('message')})
        else:
            return JsonResponse({'success': False, 'message': result.get('message')}, status=400)

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


@login_required
def get_order_status_api(request, order_id):
    """
    API endpoint to get real-time order status.
    Called by JavaScript for real-time tracking updates.
    """
    try:
        order = Order.objects.get(id=order_id, customer=request.user)
        return JsonResponse({
            'success': True,
            'status': order.status,
            'status_display': order.get_status_display(),
            'order_number': order.order_number,
            'updated_at': order.updated_at.strftime('%Y-%m-%d %H:%M:%S') if order.updated_at else None,
            'payment_status': order.payment_status,
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else None,
        })
    except Order.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Order not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def order_tracking(request, order_id):
    """
    Dedicated order tracking page with real-time status updates.
    """
    from apps.messaging.models import Conversation
    
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    # Get or create conversation with supplier
    conversation = None
    if order.product and hasattr(order.product, 'supplier'):
        conversation = Conversation.objects.filter(
            order=order,
            customer=request.user,
            supplier=order.product.supplier.user
        ).first()
    
    # Define tracking steps
    tracking_steps = [
        {'key': 'saved', 'label': 'Order Saved', 'description': 'Your order has been saved'},
        {'key': 'pending_payment', 'label': 'Pending Payment', 'description': 'Awaiting payment confirmation'},
        {'key': 'paid', 'label': 'Paid', 'description': 'Payment confirmed - order being processed'},
        {'key': 'shipped', 'label': 'Shipped', 'description': 'Order has been shipped'},
        {'key': 'complete_waiting_transport', 'label': 'Awaiting Transport', 'description': 'Waiting for transport arrangement'},
        {'key': 'completed', 'label': 'Completed', 'description': 'Order completed and delivered'},
    ]
    
    # Calculate current step index
    current_step_index = 0
    for i, step in enumerate(tracking_steps):
        if step['key'] == order.status:
            current_step_index = i
            break
    
    context = {
        'order': order,
        'tracking_steps': tracking_steps,
        'current_step_index': current_step_index,
        'conversation': conversation,
    }
    
    return render(request, 'orders/order_tracking.html', context)


@login_required
@require_http_methods(["POST"])
def mark_order_completed(request, order_id):
    """
    Mark an order as completed (for consultant/supplier to mark orders as done).
    """
    order = get_object_or_404(Order, id=order_id)
    
    # Check if user is a consultant or supplier for this order
    user_is_consultant = request.user.user_type == 'consultant'
    user_is_supplier = False
    if order.product and hasattr(order.product, 'supplier'):
        user_is_supplier = order.product.supplier.user == request.user
    
    # Also allow the customer who owns the order to mark as completed
    user_is_customer = order.customer == request.user
    
    if not (user_is_consultant or user_is_supplier or user_is_customer):
        return JsonResponse({'error': 'Unauthorized to mark this order as completed'}, status=403)
    
    # Check if order is in a valid state to be completed
    if order.status == 'completed':
        return JsonResponse({'success': True, 'message': 'Order is already completed', 'status': order.status})
    
    if order.status not in ['paid', 'shipped', 'complete_waiting_transport']:
        return JsonResponse({
            'success': False, 
            'error': f'Cannot mark order as completed. Current status is: {order.get_status_display()}'
        }, status=400)
    
    # Update order status to completed
    order.status = 'completed'
    order.save()
    
    # Send email notification to customer
    try:
        send_order_completion_email_to_customer(order)
    except Exception as e:
        print(f"Failed to send completion email: {str(e)}")
    
    return JsonResponse({
        'success': True,
        'message': f'Order #{order.order_number} marked as completed!',
        'status': order.status,
        'status_display': order.get_status_display()
    })
