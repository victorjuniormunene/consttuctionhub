from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import FileResponse, JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_http_methods
from apps.suppliers.models import Supplier
from apps.products.models import Product
from apps.orders.models import Order
from apps.consultations.models import Consultation
from apps.accounts.models import CustomUser
from django.db.models import Q
import json
from datetime import datetime

@login_required
@require_http_methods(["POST"])
def send_consultant_email(request):
    """Send email from consultant to a client"""
    try:
        data = json.loads(request.body)
        recipient_email = data.get('recipient_email')
        subject = data.get('subject')
        message = data.get('message')
        
        # Validate inputs
        if not recipient_email or not subject or not message:
            return JsonResponse({'success': False, 'error': 'All fields are required'}, status=400)
        
        # Get consultant's name for the email
        consultant = request.user
        consultant_name = consultant.get_full_name() or consultant.username
        
        # Get client name for personalized greeting
        client_name = "Valued Client"
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            client_user = User.objects.filter(email=recipient_email).first()
            if client_user:
                client_name = client_user.get_full_name() or client_user.first_name or client_user.username
        except:
            pass
        
        # Construct professional email content
        email_subject = f"{subject} - From {consultant_name} at Construction Hub"
        email_message = f"""
Dear {client_name},

Thank you for your interest in our construction services. I hope this email finds you well.

{message}

Please feel free to reach out if you have any questions or need further clarification. I am here to help you with your construction needs.

Best regards,
{consultant_name}
Consultant, Construction Hub
Email: {consultant.email}
Phone: {getattr(consultant, 'phone', 'N/A') if hasattr(consultant, 'phone') else 'N/A'}

---
This email was sent through Construction Hub. Visit us at constructionhub.com for more information.
"""
        
        # Send email
        send_mail(
            subject=email_subject,
            message=email_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        
        return JsonResponse({'success': True, 'message': 'Email sent successfully!'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def customer_dashboard_view(request):
    user = request.user

    # Ensure user has customer profile if needed (though not strictly required for dashboard)
    # Customer model exists but dashboard doesn't require it

    # Get orders for this user, excluding pending/saved orders
    orders = Order.objects.filter(
        customer=user
    ).exclude(
        status__in=['saved', 'pending_payment']
    ).order_by('-created_at')
    
    # Get pending payment orders for the Update Payment Status section
    pending_orders = Order.objects.filter(
        customer=user,
        status__in=['saved', 'pending_payment']
    ).order_by('-created_at')
    
    products = Product.objects.all()[:6]  # Show only first 6 products
    consultations = Consultation.objects.filter(customer=user).order_by('-date_requested')

    # Calculate stats
    total_orders = orders.count()
    completed_orders = orders.filter(status='completed').count()
    in_transit_orders = orders.filter(status='shipped').count()
    total_value = sum(order.total_cost or 0 for order in orders)

    context = {
        'orders': orders[:5],  # Show only recent 5 orders
        'pending_orders': pending_orders,  # Orders pending payment for manual update
        'products': products,
        'consultations': consultations[:3],  # Show only recent 3 consultations
        'order_graph': None,  # Graph disabled for now
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'in_transit_orders': in_transit_orders,
        'total_value': total_value,
    }
    return render(request, 'dashboard/customer_dashboard.html', context)

@login_required
def order_history_view(request):
    orders = Order.objects.filter(customer=request.user)
    return render(request, 'dashboard/order_history.html', {'orders': orders})

@login_required
def consultation_requests_view(request):
    consultations = Consultation.objects.filter(customer=request.user)
    return render(request, 'dashboard/consultation_requests.html', {'consultations': consultations})

@login_required
def consultant_dashboard_view(request):
    """Dashboard for users who act as consultants: show assigned consultations."""
    from apps.consultations.models import ConsultantApplication

    user = request.user

    # Restrict access: only consultants can view this page
    if user.user_type != 'consultant':
        messages.error(request, 'You must be a consultant to access the consultant dashboard.')
        return redirect('home')

    # Consultants don't need a separate profile model, just user_type check

    # Get consultant application for this user (if exists)
    consultant_app = ConsultantApplication.objects.filter(user=user, approved_at__isnull=False).first()

    # Get consultations assigned to this consultant
    assigned_consultations = Consultation.objects.filter(consultant=user).order_by('-date_requested')

    # Get pending consultations specifically
    pending_consultations = assigned_consultations.filter(status='pending')
    completed_consultations = assigned_consultations.filter(status='completed')

    # Calculate stats
    total_consultations = assigned_consultations.count()
    pending_count = pending_consultations.count()
    completed_count = completed_consultations.count()

    # Get pending orders for this consultant (if they also have supplier role)
    pending_orders_count = 0
    if user.user_type == 'supplier':
        try:
            from apps.suppliers.models import Supplier
            supplier = Supplier.objects.get(user=user)
            pending_orders_count = Order.objects.filter(
                product__supplier=supplier,
                status__in=['saved', 'pending_payment']
            ).count()
        except:
            pass

    # Get customers who have consultations with this consultant
    customers = []
    customer_ids = []
    if assigned_consultations:
        customer_ids = list(assigned_consultations.values_list('customer', flat=True).distinct())
        customers = CustomUser.objects.filter(id__in=customer_ids)

    # Get orders that can be marked as completed (for consultant's customers)
    consultant_orders = Order.objects.filter(
        customer_id__in=customer_ids,
        status__in=['paid', 'shipped', 'complete_waiting_transport']
    ).select_related('product', 'customer').order_by('-created_at')[:10]
    
    # Also get orders if consultant is also a supplier
    supplier_orders = []
    if getattr(user, 'is_supplier', False):
        try:
            supplier = Supplier.objects.get(user=user)
            supplier_orders = Order.objects.filter(
                product__supplier=supplier,
                status__in=['paid', 'shipped', 'complete_waiting_transport']
            ).select_related('customer').order_by('-created_at')[:10]
        except Supplier.DoesNotExist:
            pass
    
    # Combine unique orders
    all_consultant_orders = list(consultant_orders)
    supplier_order_ids = set(o.id for o in all_consultant_orders)
    for order in supplier_orders:
        if order.id not in supplier_order_ids:
            all_consultant_orders.append(order)

    context = {
        'consultant_app': consultant_app,
        'assigned_consultations': assigned_consultations,
        'pending_consultations': pending_consultations,
        'completed_consultations': completed_consultations,
        'total_assigned': total_consultations,
        'pending_count': pending_count,
        'completed_count': completed_count,
        'pending_orders_count': pending_orders_count,
        'customers': customers,
        'consultant_orders': all_consultant_orders,
    }
    return render(request, 'dashboard/consultant_dashboard.html', context)


@login_required(login_url='accounts:supplier_login')
def supplier_dashboard_view(request):
    """Dashboard for suppliers: show their products and orders."""
    from apps.suppliers.models import Supplier
    from apps.products.models import Product
    from apps.orders.models import Order

    user = request.user

    # Restrict access: only suppliers can view this page
    if not getattr(user, 'is_supplier', False):
        messages.error(request, 'You must be a supplier to access the supplier dashboard.')
        return redirect('accounts:supplier_login')

    # Get or create supplier profile
    supplier, created = Supplier.objects.get_or_create(
        user=user,
        defaults={
            'company_name': user.username,
            'location': '',
            'contact_number': ''
        }
    )

    if created:
        messages.info(request, 'Your supplier profile has been created. Please update your company details.')
    products = Product.objects.filter(supplier=supplier)

    # Show orders for this supplier (orders for products supplied by this supplier)
    # allow filtering by status via ?status=
    # Exclude orders created by this supplier themselves to differentiate from "Orders You Created"
    # Only show orders that have been paid or are in later stages
    status = request.GET.get('status')
    orders_qs = Order.objects.filter(
        product__supplier=supplier,
        status__in=['paid', 'shipped', 'complete_waiting_transport', 'completed']
    ).exclude(ordering_supplier=user)
    if status and status in dict(Order._meta.get_field('status').choices):
        orders_qs = orders_qs.filter(status=status)
    supplier_orders = orders_qs.order_by('-created_at')

    # Show orders created BY this supplier (supplier-created orders)
    # These are orders the supplier created for customers
    supplier_created_orders = Order.objects.filter(
        ordering_supplier=user
    ).distinct().order_by('-created_at')

    # counts per status for quick filtering UI
    from django.db import models as dj_models
    status_counts = orders_qs.values('status').order_by().annotate(count=dj_models.Count('id'))
    counts = {item['status']: item['count'] for item in status_counts}

    # All orders for this supplier's products (for the "All Orders for Your Products" section)
    # Exclude pending orders (saved and pending_payment)
    all_product_orders = Order.objects.filter(
        product__supplier=supplier
    ).exclude(
        status__in=['saved', 'pending_payment']
    ).order_by('-created_at')

    # Count completed orders for the dashboard stats
    completed_orders_count = supplier_orders.filter(status='completed').count()

    # Get unread messages count for the supplier
    from apps.messaging.models import Conversation
    unread_messages_count = 0
    try:
        supplier_conversations = Conversation.objects.filter(supplier=user)
        unread_messages_count = sum(conv.unread_count for conv in supplier_conversations)
    except:
        pass

    context = {
        'products': products,
        'supplier_orders': supplier_orders,
        'supplier_created_orders': supplier_created_orders,
        'all_product_orders': all_product_orders,
        'order_status_counts': counts,
        'selected_status': status,
        'completed_orders_count': completed_orders_count,
        'unread_messages_count': unread_messages_count,
    }
    return render(request, 'dashboard/supplier_dashboard.html', context)

def home(request):
    """Homepage: show hero, features and a small selection of featured products."""
    from apps.suppliers.models import Supplier
    from apps.consultations.models import ConsultantApplication

    # Get featured products
    featured = Product.objects.all().order_by('-pk')[:6]

    # Calculate dynamic statistics
    total_suppliers = Supplier.objects.count()
    total_customers = CustomUser.objects.filter(user_type='customer').count()
    total_consultants = ConsultantApplication.objects.filter(approved_at__isnull=False).count()

    # Format numbers with + suffix for display
    stats = {
        'suppliers': f"{total_suppliers}+",
        'customers': f"{total_customers}+",
        'consultants': f"{total_consultants}+",
        'support': "24/7"  # Static as this is a service feature
    }

    context = {
        'featured_products': featured,
        'stats': stats
    }

    return render(request, 'home.html', context)

def generate_order_graph(user, dashboard_type):
    """Generate order graph data for dashboard visualization"""
    import matplotlib
    matplotlib.use('Agg')  # Use non-GUI backend
    import matplotlib.pyplot as plt
    import base64
    from io import BytesIO
    from django.db.models import Count

    # Get orders based on dashboard type
    if dashboard_type == 'customer':
        orders = Order.objects.filter(customer=user)
    else:
        # For supplier dashboard
        from apps.suppliers.models import Supplier
        try:
            supplier = Supplier.objects.get(user=user)
            orders = Order.objects.filter(product__supplier=supplier)
        except Supplier.DoesNotExist:
            return None

    # Get status distribution
    status_counts = orders.values('status').annotate(count=Count('id')).order_by('status')

    if not status_counts:
        return None

    labels = []
    sizes = []
    colors = []

    status_colors = {
        'saved': '#ffc107',
        'paid': '#17a2b8',
        'shipped': '#007bff',
        'complete_waiting_transport': '#fd7e14',
        'completed': '#28a745',
        'canceled': '#dc3545',
    }

    for item in status_counts:
        status = item['status']
        count = item['count']
        labels.append(status.replace('_', ' ').title())
        sizes.append(count)
        colors.append(status_colors.get(status, '#6c757d'))

    # Create pie chart
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.set_title('Order Status Distribution')

    # Save to buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    # Encode to base64
    graphic = base64.b64encode(image_png).decode('utf-8')
    plt.close(fig)

    return graphic

@login_required
def download_customer_report(request):
    """Generate and download a comprehensive customer report as PDF including orders and consultations"""
    try:
        user = request.user

        # Allow all users to download customer reports for now
        # This ensures customers can always access their own data

        # Get user's orders - exclude saved and pending_payment like dashboard
        orders = Order.objects.filter(customer=user).exclude(status__in=['saved', 'pending_payment']).order_by('-created_at')

        # Get user's consultations/bookings
        consultations = Consultation.objects.filter(customer=user).order_by('-date_requested')

        # Generate PDF report
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from io import BytesIO
        from datetime import datetime

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=6,
            alignment=1  # Center alignment
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=10,
            spaceBefore=10
        )

        # Header
        elements.append(Paragraph("CONSTRUCTION HUB", title_style))
        elements.append(Paragraph("Customer Activity Report", styles['Heading2']))
        elements.append(Spacer(1, 0.3*inch))

        # Customer Information
        elements.append(Paragraph("CUSTOMER INFORMATION", heading_style))
        customer_info = [
            ['Name:', user.get_full_name() or user.username],
            ['Email:', user.email or 'N/A'],
            ['Report Generated:', datetime.now().strftime('%d/%m/%Y %H:%M')],
            ['Report Date:', datetime.now().strftime('%B %d, %Y')],
        ]
        customer_table = Table(customer_info, colWidths=[2*inch, 4*inch])
        customer_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(customer_table)
        elements.append(Spacer(1, 0.2*inch))

        # Activity Summary
        elements.append(Paragraph("ACTIVITY SUMMARY", heading_style))
        total_orders = orders.count()
        completed_orders = orders.filter(status='completed').count()
        total_consultations = consultations.count()
        completed_consultations = consultations.filter(status='completed').count()
        total_value = sum(order.total_cost or 0 for order in orders)

        summary_data = [
            ['Total Orders:', str(total_orders)],
            ['Completed Orders:', str(completed_orders)],
            ['Total Consultations:', str(total_consultations)],
            ['Completed Consultations:', str(completed_consultations)],
            ['Total Order Value:', f"KSH {total_value:,.2f}"],
        ]
        summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
        summary_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.2*inch))

        # Order Details
        if orders:
            elements.append(Paragraph("ORDER DETAILS", heading_style))
            order_data = [['Order #', 'Product', 'Quantity', 'Status', 'Date', 'Total (KSH)']]

            for order in orders:
                product_name = order.product.name if order.product else f"Plan: {order.plan_type or 'N/A'}"
                display_name = product_name[:30] + '...' if len(product_name) > 30 else product_name
                order_data.append([
                    order.order_number,
                    display_name,
                    str(order.quantity),
                    order.get_status_display(),
                    order.created_at.strftime('%d/%m/%Y'),
                    f"{order.total_cost or 0:,.2f}"
                ])

            order_table = Table(order_data, colWidths=[1*inch, 2.5*inch, 0.8*inch, 1.2*inch, 1*inch, 1*inch])
            order_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(order_table)
            elements.append(Spacer(1, 0.2*inch))
        else:
            elements.append(Paragraph("No orders found for this customer.", styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))

        # Consultation/Bookings Details
        if consultations:
            elements.append(Paragraph("CONSULTATION BOOKINGS", heading_style))
            consultation_data = [['Booking #', 'Consultant', 'Service Type', 'Status', 'Date Requested', 'Rate (KSH)']]

            for consultation in consultations:
                consultation_data.append([
                    f"CONS-{consultation.id:04d}",
                    consultation.consultant_name or 'TBD',
                    consultation.specialization or 'General Consultation',
                    consultation.get_status_display(),
                    consultation.date_requested.strftime('%d/%m/%Y'),
                    f"{consultation.consultation_rate or 0:,.2f}"
                ])

            consultation_table = Table(consultation_data, colWidths=[1*inch, 2*inch, 1.5*inch, 1*inch, 1.2*inch, 1*inch])
            consultation_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28a745')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(consultation_table)
        else:
            elements.append(Paragraph("No consultation bookings found for this customer.", styles['Normal']))

        # Key Points Section
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("KEY POINTS & REMINDERS", heading_style))
        key_points = [
            "• Keep this report for your records and tax purposes",
            "• Contact suppliers directly for order status updates",
            "• Rate your experience to help improve our services",
            "• All payments are processed securely through M-Pesa",
            "• Orders typically ship within 2-3 business days",
            "• Consultations are scheduled based on consultant availability",
            f"• Report generated on: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}",
        ]

        for point in key_points:
            elements.append(Paragraph(point, styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))

        # Footer
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("Thank you for choosing Construction Hub!", styles['Normal']))
        elements.append(Paragraph("For support, contact us at support@constructionhub.com", styles['Normal']))

        # Build PDF
        doc.build(elements)
        buffer.seek(0)

        # Return as file download
        response = FileResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="customer_activity_report_{user.username}_{datetime.now().strftime("%Y%m%d")}.pdf"'
        return response

    except Exception as e:
        messages.error(request, f'Error generating report: {str(e)}')
        return redirect('home')

@login_required
def download_supplier_report(request):
    """Generate and download a supplier report as PDF showing orders from customers"""
    try:
        user = request.user

        # Check if user is a supplier
        if user.user_type != 'supplier':
            messages.error(request, 'You must be a supplier to access this report.')
            return redirect('accounts:dashboard')

        from apps.suppliers.models import Supplier
        supplier = Supplier.objects.get(user=user)

        # Get orders for this supplier's products - only paid/processed orders, exclude supplier-created orders
        orders = Order.objects.filter(
            product__supplier=supplier,
            status__in=['paid', 'shipped', 'complete_waiting_transport', 'completed']
        ).exclude(ordering_supplier=user).order_by('-created_at')

        # Generate PDF report
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from io import BytesIO
        from datetime import datetime

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=6,
            alignment=1  # Center alignment
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=10,
            spaceBefore=10
        )

        # Header
        elements.append(Paragraph("CONSTRUCTION HUB", title_style))
        elements.append(Paragraph("Supplier Order Report", styles['Heading2']))
        elements.append(Spacer(1, 0.3*inch))

        # Supplier Information
        elements.append(Paragraph("SUPPLIER INFORMATION", heading_style))
        supplier_info = [
            ['Company Name:', supplier.company_name],
            ['Contact Person:', user.get_full_name() or user.username],
            ['Email:', user.email or 'N/A'],
            ['Phone:', supplier.contact_number or 'N/A'],
            ['Report Generated:', datetime.now().strftime('%d/%m/%Y %H:%M')],
            ['Report Date:', datetime.now().strftime('%B %d, %Y')],
        ]
        supplier_table = Table(supplier_info, colWidths=[2*inch, 4*inch])
        supplier_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(supplier_table)
        elements.append(Spacer(1, 0.2*inch))

        # Order Summary
        elements.append(Paragraph("ORDER SUMMARY", heading_style))
        total_orders = orders.count()
        completed_orders = orders.filter(status='completed').count()
        pending_orders = orders.filter(status='saved').count()
        paid_orders = orders.filter(status='paid').count()
        total_value = sum(order.total_cost for order in orders)

        summary_data = [
            ['Total Orders:', str(total_orders)],
            ['Completed Orders:', str(completed_orders)],
            ['Pending Orders:', str(pending_orders)],
            ['Paid Orders:', str(paid_orders)],
            ['Total Revenue:', f"KSH {total_value:,.2f}"],
        ]
        summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
        summary_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.2*inch))

        # Order Details
        if orders:
            elements.append(Paragraph("CUSTOMER ORDERS", heading_style))
            order_data = [['Order #', 'Customer', 'Product', 'Quantity', 'Status', 'Date', 'Total (KSH)']]

            for order in orders:
                customer_name = order.customer_name or (order.customer.get_full_name() if order.customer else 'N/A')
                order_data.append([
                    order.order_number,
                    customer_name[:20] + '...' if len(customer_name) > 20 else customer_name,
                    order.product.name[:25] + '...' if len(order.product.name) > 25 else order.product.name,
                    str(order.quantity),
                    order.get_status_display(),
                    order.created_at.strftime('%d/%m/%Y'),
                    f"{order.total_cost:,.2f}"
                ])

            order_table = Table(order_data, colWidths=[1*inch, 1.5*inch, 2*inch, 0.8*inch, 1.2*inch, 1*inch, 1.2*inch])
            order_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(order_table)
        else:
            elements.append(Paragraph("No orders found for this supplier.", styles['Normal']))

        # Key Points Section
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("KEY POINTS & REMINDERS", heading_style))
        key_points = [
            "• Process orders promptly to maintain customer satisfaction",
            "• Contact customers directly for order clarifications",
            "• Update order status regularly in the system",
            "• All payments are processed through M-Pesa for security",
            "• Keep detailed records for accounting and tax purposes",
            "• Respond to customer inquiries within 24 hours",
            f"• Report generated on: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}",
        ]

        for point in key_points:
            elements.append(Paragraph(point, styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))

        # Footer
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("Thank you for being a valued Construction Hub supplier!", styles['Normal']))
        elements.append(Paragraph("For support, contact us at suppliers@constructionhub.com", styles['Normal']))

        # Build PDF
        doc.build(elements)
        buffer.seek(0)

        # Return as file download
        response = FileResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="supplier_orders_report_{supplier.company_name}_{datetime.now().strftime("%Y%m%d")}.pdf"'
        return response

    except Exception as e:
        messages.error(request, f'Error generating supplier report: {str(e)}')
        return redirect('accounts:dashboard')

@login_required
def download_consultant_report(request):
    """Generate and download a consultant report as PDF showing bookings from customers"""
    try:
        user = request.user

        # Check if user is a consultant
        if user.user_type != 'consultant':
            messages.error(request, 'You must be a consultant to download consultant reports.')
            return redirect('accounts:dashboard')

        # Get consultations assigned to this consultant
        consultations = Consultation.objects.filter(consultant=user).order_by('-date_requested')

        # Generate PDF report
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from io import BytesIO
        from datetime import datetime

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=6,
            alignment=1  # Center alignment
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=10,
            spaceBefore=10
        )

        # Header
        elements.append(Paragraph("CONSTRUCTION HUB", title_style))
        elements.append(Paragraph("Consultant Bookings Report", styles['Heading2']))
        elements.append(Spacer(1, 0.3*inch))

        # Consultant Information
        elements.append(Paragraph("CONSULTANT INFORMATION", heading_style))
        consultant_info = [
            ['Name:', user.get_full_name() or user.username],
            ['Email:', user.email or 'N/A'],
            ['Specialization:', getattr(user, 'specialization', 'General Construction')],
            ['Report Generated:', datetime.now().strftime('%d/%m/%Y %H:%M')],
            ['Report Date:', datetime.now().strftime('%B %d, %Y')],
        ]
        consultant_table = Table(consultant_info, colWidths=[2*inch, 4*inch])
        consultant_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(consultant_table)
        elements.append(Spacer(1, 0.2*inch))

        # Bookings Summary
        elements.append(Paragraph("BOOKINGS SUMMARY", heading_style))
        total_bookings = consultations.count()
        completed_bookings = consultations.filter(status='completed').count()
        pending_bookings = consultations.filter(status='pending').count()
        total_revenue = sum(consultation.consultation_rate or 0 for consultation in consultations)

        summary_data = [
            ['Total Bookings:', str(total_bookings)],
            ['Completed Consultations:', str(completed_bookings)],
            ['Pending Consultations:', str(pending_bookings)],
            ['Total Revenue:', f"KSH {total_revenue:,.2f}"],
        ]
        summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
        summary_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.2*inch))

        # Bookings Details
        if consultations:
            elements.append(Paragraph("CUSTOMER BOOKINGS", heading_style))
            booking_data = [['Booking #', 'Customer', 'Service Type', 'Status', 'Date Requested', 'Rate (KSH)']]

            for consultation in consultations:
                customer_name = consultation.customer.get_full_name() if consultation.customer else 'N/A'
                booking_data.append([
                    f"CONS-{consultation.id:04d}",
                    customer_name[:20] + '...' if len(customer_name) > 20 else customer_name,
                    consultation.specialization or 'General Consultation',
                    consultation.get_status_display(),
                    consultation.date_requested.strftime('%d/%m/%Y'),
                    f"{consultation.consultation_rate or 0:,.2f}"
                ])

            booking_table = Table(booking_data, colWidths=[1*inch, 1.5*inch, 2*inch, 1*inch, 1.2*inch, 1.2*inch])
            booking_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28a745')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(booking_table)
        else:
            elements.append(Paragraph("No consultation bookings found for this consultant.", styles['Normal']))

        # Key Points Section
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("KEY POINTS & REMINDERS", heading_style))
        key_points = [
            "• Prepare thoroughly for each consultation session",
            "• Contact customers in advance to confirm appointment details",
            "• Update booking status after each consultation",
            "• Provide detailed feedback and recommendations",
            "• Maintain professional standards and expertise",
            "• Keep accurate records for billing and follow-up",
            f"• Report generated on: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}",
        ]

        for point in key_points:
            elements.append(Paragraph(point, styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))

        # Footer
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("Thank you for being a valued Construction Hub consultant!", styles['Normal']))
        elements.append(Paragraph("For support, contact us at consultants@constructionhub.com", styles['Normal']))

        # Build PDF
        doc.build(elements)
        buffer.seek(0)

        # Return as file download
        response = FileResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="consultant_bookings_report_{user.username}_{datetime.now().strftime("%Y%m%d")}.pdf"'
        return response

    except Exception as e:
        messages.error(request, f'Error generating consultant report: {str(e)}')
        return redirect('home')

@login_required
def download_supplier_consolidated_report(request):
    """Generate and download a comprehensive consolidated supplier report as PDF showing all orders with full customer details"""
    try:
        user = request.user

        # Check if user is a supplier
        if user.user_type != 'supplier':
            messages.error(request, 'You must be a supplier to access this report.')
            return redirect('accounts:dashboard')

        from apps.suppliers.models import Supplier
        supplier = Supplier.objects.get(user=user)

        # Get all orders for this supplier's products
        orders = Order.objects.filter(product__supplier=supplier).order_by('-created_at')

        # Generate comprehensive PDF report
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from io import BytesIO
        from datetime import datetime

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=6,
            alignment=1  # Center alignment
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=10,
            spaceBefore=10
        )
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#2e7d32'),
            spaceAfter=8,
            spaceBefore=8
        )

        # Header
        elements.append(Paragraph("CONSTRUCTION HUB", title_style))
        elements.append(Paragraph("Comprehensive Supplier Order Report", styles['Heading2']))
        elements.append(Spacer(1, 0.3*inch))

        # Report Information
        elements.append(Paragraph("REPORT INFORMATION", heading_style))
        report_info = [
            ['Report Type:', 'Consolidated Supplier Order Report'],
            ['Generated For:', supplier.company_name or user.get_full_name()],
            ['Supplier ID:', f'SUP-{supplier.id:04d}'],
            ['Report Generated:', datetime.now().strftime('%d/%m/%Y %H:%M')],
            ['Report Date:', datetime.now().strftime('%B %d, %Y')],
            ['Time Period:', 'All Orders'],
            ['Total Orders:', str(orders.count())],
        ]
        report_table = Table(report_info, colWidths=[2.5*inch, 4*inch])
        report_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(report_table)
        elements.append(Spacer(1, 0.2*inch))

        # Supplier Information
        elements.append(Paragraph("SUPPLIER DETAILS", heading_style))
        supplier_info = [
            ['Company Name:', supplier.company_name],
            ['Contact Person:', user.get_full_name() or user.username],
            ['Email:', user.email or 'N/A'],
            ['Phone:', supplier.contact_number or 'N/A'],
            ['Location:', supplier.location or 'N/A'],
            ['Registration Date:', supplier.created_at.strftime('%d/%m/%Y') if hasattr(supplier, 'created_at') else 'N/A'],
        ]
        supplier_table = Table(supplier_info, colWidths=[2.5*inch, 4*inch])
        supplier_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(supplier_table)
        elements.append(Spacer(1, 0.2*inch))

        # Order Summary Statistics
        elements.append(Paragraph("ORDER SUMMARY STATISTICS", heading_style))
        total_orders = orders.count()
        completed_orders = orders.filter(status='completed').count()
        pending_orders = orders.filter(status='saved').count()
        paid_orders = orders.filter(status='paid').count()
        shipped_orders = orders.filter(status='shipped').count()
        canceled_orders = orders.filter(status='canceled').count()
        total_revenue = sum(order.total_cost for order in orders)
        total_quantity = sum(order.quantity for order in orders)

        summary_data = [
            ['Total Orders:', str(total_orders)],
            ['Completed Orders:', str(completed_orders)],
            ['Pending Orders:', str(pending_orders)],
            ['Paid Orders:', str(paid_orders)],
            ['Shipped Orders:', str(shipped_orders)],
            ['Canceled Orders:', str(canceled_orders)],
            ['Total Quantity Sold:', f"{total_quantity} units"],
            ['Total Revenue:', f"KSH {total_revenue:,.2f}"],
            ['Average Order Value:', f"KSH {total_revenue/total_orders:,.2f}" if total_orders > 0 else "KSH 0.00"],
        ]
        summary_table = Table(summary_data, colWidths=[2.5*inch, 4*inch])
        summary_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.2*inch))

        # Detailed Order Information
        if orders:
            elements.append(Paragraph("DETAILED ORDER INFORMATION", heading_style))
            elements.append(Paragraph("Complete list of all customer orders with full details", subheading_style))

            # Order Details Table
            order_data = [['Order #', 'Date', 'Customer Details', 'Product', 'Qty', 'Unit Price', 'Total', 'Status']]

            for order in orders:
                customer_details = f"{order.customer_name}\n{order.customer_number}\n{order.customer_location}"
                order_data.append([
                    order.order_number,
                    order.created_at.strftime('%d/%m/%Y\n%H:%M'),
                    customer_details,
                    order.product.name[:25] + '...' if len(order.product.name) > 25 else order.product.name,
                    str(order.quantity),
                    f"KSH {order.price:,.2f}",
                    f"KSH {order.total_cost:,.2f}",
                    order.get_status_display()
                ])

            order_table = Table(order_data, colWidths=[1*inch, 1.2*inch, 2*inch, 1.5*inch, 0.6*inch, 1*inch, 1*inch, 1*inch])
            order_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (2, 1), (2, -1), 'LEFT'),  # Customer details left-aligned
            ]))
            elements.append(order_table)
            elements.append(Spacer(1, 0.3*inch))

            # Customer Analysis Section
            elements.append(Paragraph("CUSTOMER ANALYSIS", heading_style))

            # Top Customers by Order Value
            customer_totals = {}
            for order in orders:
                customer_key = order.customer_name or "Unknown Customer"
                if customer_key not in customer_totals:
                    customer_totals[customer_key] = {'orders': 0, 'total': 0, 'quantity': 0}
                customer_totals[customer_key]['orders'] += 1
                customer_totals[customer_key]['total'] += order.total_cost
                customer_totals[customer_key]['quantity'] += order.quantity

            top_customers = sorted(customer_totals.items(), key=lambda x: x[1]['total'], reverse=True)[:10]

            if top_customers:
                elements.append(Paragraph("Top Customers by Order Value", subheading_style))
                customer_data = [['Customer Name', 'Orders', 'Total Quantity', 'Total Value']]
                for customer_name, data in top_customers:
                    customer_data.append([
                        customer_name[:30] + '...' if len(customer_name) > 30 else customer_name,
                        str(data['orders']),
                        str(data['quantity']),
                        f"KSH {data['total']:,.2f}"
                    ])

                customer_table = Table(customer_data, colWidths=[2.5*inch, 1*inch, 1.2*inch, 1.5*inch])
                customer_table.setStyle(TableStyle([
                    ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                    ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28a745')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                elements.append(customer_table)
                elements.append(Spacer(1, 0.2*inch))

            # Product Performance
            product_totals = {}
            for order in orders:
                product_name = order.product.name
                if product_name not in product_totals:
                    product_totals[product_name] = {'orders': 0, 'quantity': 0, 'revenue': 0}
                product_totals[product_name]['orders'] += 1
                product_totals[product_name]['quantity'] += order.quantity
                product_totals[product_name]['revenue'] += order.total_cost

            top_products = sorted(product_totals.items(), key=lambda x: x[1]['revenue'], reverse=True)[:10]

            if top_products:
                elements.append(Paragraph("Product Performance Analysis", subheading_style))
                product_data = [['Product Name', 'Orders', 'Units Sold', 'Revenue']]
                for product_name, data in top_products:
                    product_data.append([
                        product_name[:35] + '...' if len(product_name) > 35 else product_name,
                        str(data['orders']),
                        str(data['quantity']),
                        f"KSH {data['revenue']:,.2f}"
                    ])

                product_table = Table(product_data, colWidths=[2.5*inch, 1*inch, 1.2*inch, 1.5*inch])
                product_table.setStyle(TableStyle([
                    ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                    ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff7f31')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                elements.append(product_table)
                elements.append(Spacer(1, 0.2*inch))

        else:
            elements.append(Paragraph("No orders found for this supplier.", styles['Normal']))

        # Key Performance Indicators
        elements.append(Paragraph("KEY PERFORMANCE INDICATORS", heading_style))
        kpi_data = [
            ['Conversion Rate:', f"{(paid_orders/total_orders*100):.1f}%" if total_orders > 0 else "0%"],
            ['Completion Rate:', f"{(completed_orders/total_orders*100):.1f}%" if total_orders > 0 else "0%"],
            ['Average Order Size:', f"{total_quantity/total_orders:.1f} units" if total_orders > 0 else "0 units"],
            ['Revenue per Order:', f"KSH {total_revenue/total_orders:,.2f}" if total_orders > 0 else "KSH 0.00"],
        ]
        kpi_table = Table(kpi_data, colWidths=[2.5*inch, 4*inch])
        kpi_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(kpi_table)
        elements.append(Spacer(1, 0.2*inch))

        # Recommendations Section
        elements.append(Paragraph("BUSINESS RECOMMENDATIONS", heading_style))
        recommendations = [
            "• Focus marketing efforts on your top-performing products",
            "• Follow up with customers who have pending orders",
            "• Consider loyalty programs for your best customers",
            "• Optimize inventory based on product performance data",
            "• Improve order fulfillment time to increase customer satisfaction",
            f"• This report covers all {total_orders} orders and KSH {total_revenue:,.2f} in revenue",
        ]

        for rec in recommendations:
            elements.append(Paragraph(rec, styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))

        # Footer
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("Thank you for being a valued Construction Hub supplier!", styles['Normal']))
        elements.append(Paragraph("This comprehensive report provides complete visibility into your business performance.", styles['Normal']))
        elements.append(Paragraph(f"Report generated on: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}", styles['Normal']))

        # Build PDF
        doc.build(elements)
        buffer.seek(0)

        # Return as file download
        response = FileResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="comprehensive_supplier_report_{supplier.company_name}_{datetime.now().strftime("%Y%m%d")}.pdf"'
        return response

    except Exception as e:
        messages.error(request, f'Error generating comprehensive supplier report: {str(e)}')
        return redirect('accounts:dashboard')
