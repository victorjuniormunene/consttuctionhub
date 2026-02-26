from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import ConsultantApplication, Consultation
from .forms import ConsultationForm
from apps.accounts.models import CustomUser
from django.template.loader import render_to_string
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
import datetime
from .pdf_utils import generate_qualification_form_pdf, generate_user_profile_pdf
from django.conf import settings
from django.core.mail import send_mail
import json
import logging


def download_qualification_form(request):
    """
    Download the consultant qualification form as PDF.
    """
    # Generate the PDF
    buffer = generate_qualification_form_pdf()
    
    # Create HTTP response with PDF content
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="qualification_form.pdf"'
    return response


@login_required
def download_profile_pdf(request):
    """
    Download the user profile PDF for Smart Construction Hub.
    """
    buffer = generate_user_profile_pdf(request.user)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    filename = f"profile_{request.user.username}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def select_consultant(request):
    """Step 1: Customer selects a consultant from available options"""
    # Prevent consultants from booking consultations
    if getattr(request.user, 'is_consultant', False):
        from django.contrib import messages
        messages.error(request, 'As a consultant, you cannot book consultations. Please contact support if you need assistance.')
        return redirect('accounts:dashboard')

    consultants = ConsultantApplication.objects.filter(processed=True, approved_at__isnull=False)
    specializations = ConsultantApplication.objects.filter(processed=True, approved_at__isnull=False).exclude(specialization__isnull=True).exclude(specialization='').values_list('specialization', flat=True).distinct()
    selected_specialization = request.GET.get('specialization', '')

    if selected_specialization:
        consultants = consultants.filter(specialization=selected_specialization)

    return render(request, 'consultations/select_consultant.html', {
        'consultants': consultants,
        'specializations': specializations,
        'selected_specialization': selected_specialization
    })


@login_required
def confirm_consultation_booking(request, consultant_id):
    """Step 2: Confirm booking details and redirect to payment"""
    # Prevent consultants from booking consultations
    if getattr(request.user, 'is_consultant', False):
        from django.contrib import messages
        messages.error(request, 'As a consultant, you cannot book consultations. Please contact support if you need assistance.')
        return redirect('accounts:dashboard')

    consultant = get_object_or_404(ConsultantApplication, id=consultant_id)

    if request.method == 'POST':
        # Instead of creating the consultation here, redirect to payment
        # The payment view will create the consultation with status='pending_payment'
        # and the booking will only be confirmed after successful payment
        return redirect('consultations:consultation_payment', consultant_id=consultant_id)

    return render(request, 'consultations/confirm_consultation.html', {
        'consultant': consultant
    })


@login_required
def consultation_success(request, consultation_id):
    """Step 3: Show receipt after successful booking"""
    consultation = get_object_or_404(Consultation, id=consultation_id)
    
    # Verify user is the customer who made the booking
    if consultation.customer != request.user:
        return redirect('home')
    
    return render(request, 'consultations/consultation_success.html', {
        'consultation': consultation
    })


@login_required
@require_http_methods(["POST"])
def mark_consultation_completed(request, consultation_id):
    """Mark a consultation as completed"""
    from django.contrib import messages
    from django.core.mail import send_mail
    from django.conf import settings
    
    consultation = get_object_or_404(Consultation, id=consultation_id)
    
    # Verify user is the consultant assigned to this consultation
    # Check by consultant user or by consultant_name matching the consultant's application name
    is_authorized = False
    
    # Check if user is the assigned consultant
    if consultation.consultant == request.user:
        is_authorized = True
    # Also check by consultant name (for cases where consultant was stored by name)
    elif request.user.user_type == 'consultant':
        consultant_app = request.user.consultant_applications.filter(approved_at__isnull=False).first()
        if consultant_app and consultation.consultant_name == consultant_app.full_name:
            is_authorized = True
    
    if not is_authorized:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # Update status to completed
    old_status = consultation.status
    consultation.status = 'completed'
    consultation.save()
    
    # Send notification email to customer
    try:
        subject = f'Consultation Completed - Booking #{consultation.id}'
        message = f"""
Dear {consultation.customer.get_full_name() or consultation.customer.username},

Your consultation session with {consultation.consultant_name} has been marked as COMPLETED!

Booking Details:
- Consultant: {consultation.consultant_name}
- Specialization: {consultation.specialization or 'General Consultation'}
- Date Completed: {consultation.date_requested.strftime('%B %d, %Y')}
- Booking ID: #{consultation.id}

Your consultation has been successfully completed. Thank you for using Construction Hub services.

If you have any feedback or need further assistance, please don't hesitate to contact us.

Best regards,
Construction Hub Team
"""
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [consultation.customer.email],
            fail_silently=True,
        )
    except Exception as e:
        # Log error but don't fail the main operation
        import logging
        logging.getLogger(__name__).error(f"Failed to send completion email: {e}")
    
    return JsonResponse({
        'success': True,
        'message': f'Consultation #{consultation.id} marked as completed',
        'new_status': consultation.status
    })


@login_required
def download_consultation_receipt(request, consultation_id):
    """Download consultation receipt as PDF"""
    consultation = get_object_or_404(Consultation, id=consultation_id)
    
    # Verify user is the customer
    if consultation.customer != request.user:
        return HttpResponse("Unauthorized", status=403)
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=6,
        spaceBefore=6
    )
    
    normal_style = styles['Normal']
    
    # Title
    elements.append(Paragraph("CONSULTATION RECEIPT", title_style))
    elements.append(Spacer(1, 12))
    
    # Receipt details
    receipt_data = [
        ['Booking ID:', f'#{consultation.id}'],
        ['Date:', consultation.date_requested.strftime('%B %d, %Y')],
        ['Status:', consultation.status.upper()],
    ]
    
    receipt_table = Table(receipt_data, colWidths=[2*inch, 3*inch])
    receipt_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 11),
        ('FONT', (1, 0), (1, -1), 'Helvetica', 11),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(receipt_table)
    elements.append(Spacer(1, 12))
    
    # Consultant information
    elements.append(Paragraph("CONSULTANT INFORMATION", heading_style))
    consultant_data = [
        ['Name:', consultation.consultant_name or 'N/A'],
        ['Phone:', consultation.consultant_phone or 'N/A'],
        ['Specialization:', consultation.specialization or 'N/A'],
    ]
    
    consultant_table = Table(consultant_data, colWidths=[2*inch, 3*inch])
    consultant_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 11),
        ('FONT', (1, 0), (1, -1), 'Helvetica', 11),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(consultant_table)
    elements.append(Spacer(1, 12))
    
    # Pricing
    elements.append(Paragraph("PRICING", heading_style))
    pricing_data = [
        ['Consultation Rate (KSH):', f'KSH {consultation.consultation_rate:,.2f}'],
    ]
    
    pricing_table = Table(pricing_data, colWidths=[2*inch, 3*inch])
    pricing_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 11),
        ('FONT', (1, 0), (1, -1), 'Helvetica-Bold', 12),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(pricing_table)
    elements.append(Spacer(1, 12))
    
    # Additional details
    if consultation.details:
        elements.append(Paragraph("BOOKING DETAILS", heading_style))
        elements.append(Paragraph(consultation.details, normal_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="consultation_receipt_{consultation.id}.pdf"'
    return response


@login_required
def download_order_receipt_customer(request, order_id):
    """Download order receipt as PDF for customers"""
    from apps.orders.models import Order
    
    order = get_object_or_404(Order, id=order_id)
    
    # Verify user is the customer
    if order.customer != request.user:
        return HttpResponse("Unauthorized", status=403)
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=6,
        spaceBefore=6
    )
    
    normal_style = styles['Normal']
    
    # Title
    elements.append(Paragraph("ORDER RECEIPT", title_style))
    elements.append(Spacer(1, 12))
    
    # Order details
    order_data = [
        ['Order ID:', f'#{order.id}'],
        ['Date:', order.created_at.strftime('%B %d, %Y')],
        ['Status:', order.status.upper()],
    ]
    
    order_table = Table(order_data, colWidths=[2*inch, 3*inch])
    order_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 11),
        ('FONT', (1, 0), (1, -1), 'Helvetica', 11),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(order_table)
    elements.append(Spacer(1, 12))
    
    # Items
    elements.append(Paragraph("ORDER ITEMS", heading_style))
    items_data = [['Product', 'Quantity', 'Unit Price (KSH)', 'Total (KSH)']]
    total_amount = 0
    
    # Order model has a single product, not multiple items
    amount = order.quantity * order.price
    total_amount += amount
    items_data.append([
        order.product.name,
        str(order.quantity),
        f"KSH {order.price:,.2f}",
        f"KSH {amount:,.2f}"
    ])
    
    items_table = Table(items_data, colWidths=[2.5*inch, 1*inch, 1.5*inch, 1.5*inch])
    items_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 11),
        ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 12))
    
    # Total
    total_data = [
        ['TOTAL (KSH):', f'KSH {total_amount:,.2f}']
    ]
    total_table = Table(total_data, colWidths=[2*inch, 3*inch])
    total_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica-Bold', 12),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f0f0')),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(total_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_receipt_{order.id}.pdf"'
    return response


@login_required
def consultation_payment(request, consultant_id):
    """Initiate M-Pesa payment for consultation booking"""
    from django.contrib import messages
    
    consultant = get_object_or_404(ConsultantApplication, id=consultant_id)
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        
        if not phone_number:
            messages.error(request, 'Please provide your M-Pesa phone number.')
            return redirect('consultations:consultation_payment', consultant_id=consultant_id)
        
        # Create a pending consultation record (will be confirmed after payment)
        consultation = Consultation.objects.create(
            customer=request.user,
            consultant_id=consultant.user_id,
            consultant_name=consultant.full_name,
            consultant_phone=consultant.phone,
            consultation_rate=consultant.consultation_rate,
            specialization=consultant.specialization,
            details=request.POST.get('details', ''),
            status='pending_payment'  # Waiting for payment
        )
        
        # Initiate M-Pesa payment
        from apps.orders.mpesa_utils import initiate_mpesa_payment_for_amount
        
        amount = float(consultation.consultation_rate)
        reference = f"CONSULT-{consultation.id}"
        
        result = initiate_mpesa_payment_for_amount(
            amount=amount,
            phone_number=phone_number,
            reference=reference
        )
        
        if result.get('success'):
            # Save checkout request ID to consultation
            consultation.mpesa_checkout_request_id = result.get('checkout_request_id')
            consultation.mpesa_phone_number = phone_number
            consultation.save()
            
            messages.success(request, f'Payment initiated! Please check your phone and enter your PIN to complete the payment.')
            return redirect('consultations:consultation_success', consultation_id=consultation.id)
        else:
            # Payment failed, delete the consultation
            consultation.delete()
            messages.error(request, f'Failed to initiate payment: {result.get("error", "Unknown error")}')
            return redirect('consultations:consultation_payment', consultant_id=consultant_id)
    
    return render(request, 'consultations/payment.html', {
        'consultant': consultant
    })


@csrf_exempt
def consultation_mpesa_callback(request):
    """Handle M-Pesa callback for consultation payments"""
    logger = logging.getLogger(__name__)
    
    if request.method == 'POST':
        try:
            callback_data = json.loads(request.body.decode('utf-8'))
            logger.info(f"Consultation M-Pesa callback received: {callback_data}")
            
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
                
                # Find the consultation with this checkout request ID
                try:
                    consultation = Consultation.objects.get(mpesa_checkout_request_id=checkout_request_id)
                    
                    # Update consultation status
                    consultation.status = 'scheduled'
                    consultation.mpesa_transaction_id = transaction_id
                    consultation.mpesa_phone_number = phone_number
                    consultation.save()
                    
                    # Send notification to consultant
                    subject = f'New Consultation Booking - Payment Confirmed'
                    message = f"""
                    Dear {consultation.consultant_name},

                    A customer has booked a consultation with you and completed payment.

                    Booking Details:
                    - Customer: {consultation.customer.username} ({consultation.customer.email})
                    - Booking ID: #{consultation.id}
                    - Date Requested: {consultation.date_requested.strftime('%B %d, %Y %H:%M')}
                    - Specialization: {consultation.specialization or 'General'}
                    - Rate: KSH {consultation.consultation_rate}
                    - Payment Transaction ID: {transaction_id}
                    - Details: {consultation.details or 'No additional details provided'}

                    Please log in to your dashboard to manage this consultation.

                    Best regards,
                    Construction Hub Team
                    """
                    
                    try:
                        if consultation.consultant:
                            send_mail(
                                subject,
                                message,
                                settings.DEFAULT_FROM_EMAIL,
                                [consultation.consultant.email],
                                fail_silently=False,
                            )
                            logger.info(f"Consultation notification email sent to consultant for booking #{consultation.id}")
                    except Exception as e:
                        logger.error(f"Failed to send email to consultant: {e}")
                    
                    # Send confirmation email to customer
                    customer_subject = f'Consultation Booking Confirmed - Payment Received'
                    customer_message = f"""
                    Dear {consultation.customer.username},

                    Your consultation booking has been confirmed and payment received!

                    Booking Details:
                    - Consultant: {consultation.consultant_name}
                    - Specialization: {consultation.specialization or 'General'}
                    - Consultation Rate: KSH {consultation.consultation_rate}
                    - Date Requested: {consultation.date_requested.strftime('%B %d, %Y %H:%M')}
                    - Booking ID: #{consultation.id}
                    - Payment Transaction ID: {transaction_id}
                    - Status: {consultation.status.upper()}

                    Your Notes: {consultation.details or 'No additional details provided'}

                    The consultant will contact you soon to schedule the consultation session.

                    You can view your booking details in your dashboard.

                    Best regards,
                    Construction Hub Team
                    """
                    
                    try:
                        send_mail(
                            customer_subject,
                            customer_message,
                            settings.DEFAULT_FROM_EMAIL,
                            [consultation.customer.email],
                            fail_silently=False,
                        )
                        logger.info(f"Confirmation email sent to customer for booking #{consultation.id}")
                    except Exception as e:
                        logger.error(f"Failed to send email to customer: {e}")
                    
                    return JsonResponse({'success': True, 'message': 'Consultation payment processed successfully'})
                    
                except Consultation.DoesNotExist:
                    logger.error(f"Consultation not found for checkout_request_id: {checkout_request_id}")
                    return JsonResponse({'success': False, 'message': 'Consultation not found'}, status=404)
                    
            else:
                # Payment failed
                checkout_request_id = stk_callback.get('CheckoutRequestID')
                try:
                    consultation = Consultation.objects.get(mpesa_checkout_request_id=checkout_request_id)
                    consultation.status = 'canceled'
                    consultation.save()
                    logger.info(f"Consultation payment failed, booking #{consultation.id} canceled")
                except Consultation.DoesNotExist:
                    pass
                
                return JsonResponse({
                    'success': False,
                    'message': f"Payment failed: {stk_callback.get('ResultDesc', 'Unknown error')}"
                }, status=400)
                
        except Exception as e:
            logger.error(f"Error processing consultation callback: {e}")
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)
