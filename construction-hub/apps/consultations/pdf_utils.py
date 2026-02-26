"""
PDF generation utilities for consultant receipts and order receipts.
"""
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from datetime import datetime


def generate_consultant_receipt_pdf(application):
    """
    Generate a consultant application receipt PDF.
    
    Args:
        application: ConsultantApplication instance
    
    Returns:
        BytesIO object containing the PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Create styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#ff7f31'),
        spaceAfter=12,
        alignment=1  # center
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        spaceAfter=8,
        spaceBefore=12
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6
    )
    
    # Build story
    story = []
    
    # Header
    story.append(Paragraph("CONSULTANT APPLICATION RECEIPT", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Receipt info table
    receipt_data = [
        ['Receipt Number:', f'APP-{application.id:08d}'],
        ['Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
    ]
    receipt_table = Table(receipt_data, colWidths=[2*inch, 4.5*inch])
    receipt_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(receipt_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Applicant Information
    story.append(Paragraph("APPLICANT INFORMATION", heading_style))
    applicant_data = [
        ['Full Name:', application.full_name],
        ['Email:', application.email],
        ['Phone Number:', application.phone or 'N/A'],
        ['Specialization:', application.specialization or 'Not specified'],
        ['Experience (Years):', str(application.experience_years)],
    ]
    applicant_table = Table(applicant_data, colWidths=[2*inch, 4.5*inch])
    applicant_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(applicant_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Application Details
    if application.cover_letter:
        story.append(Paragraph("COVER LETTER", heading_style))
        story.append(Paragraph(application.cover_letter[:500] + ('...' if len(application.cover_letter) > 500 else ''), normal_style))
        story.append(Spacer(1, 0.1*inch))
    
    # Submission timestamp
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(
        f"Submitted on: {application.submitted_at.strftime('%B %d, %Y at %H:%M:%S')}",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#999999'), alignment=1)
    ))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_user_profile_pdf(user):
    """
    Generate a comprehensive user profile PDF for Smart Construction Hub.
    Includes all user data across multiple pages: profile info, orders, products, consultations, plan purchases, cart, and contact messages.
    
    Args:
        user: CustomUser instance
    
    Returns:
        BytesIO object containing the PDF
    """
    from apps.suppliers.models import Supplier
    from apps.orders.models import Order, Cart
    from apps.products.models import Product
    from apps.accounts.models import PlanPurchase, ContactMessage
    from apps.consultations.models import Consultation
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Create styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#ff7f31'),
        spaceAfter=12,
        alignment=1
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        spaceAfter=8,
        spaceBefore=12
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6
    )
    
    # Build story - multi-page PDF
    story = []
    
    # ==================== PAGE 1: PROFILE INFORMATION ====================
    story.append(Paragraph("SMART CONSTRUCTION HUB", title_style))
    story.append(Paragraph("USER PROFILE REPORT", ParagraphStyle('SubTitle', parent=styles['Heading2'], fontSize=16, textColor=colors.HexColor('#666666'), alignment=1, spaceAfter=20)))
    story.append(Spacer(1, 0.2*inch))
    
    # Profile Information Section
    story.append(Paragraph("PROFILE INFORMATION", heading_style))
    
    # Get profile data based on user type
    profile_data = [
        ['Username:', user.username],
        ['Email:', user.email],
        ['Full Name:', f"{user.first_name} {user.last_name}".strip() or 'N/A'],
        ['Phone Number:', user.phone_number or 'N/A'],
        ['Company Name:', user.company_name or 'N/A'],
        ['Location:', user.location or 'N/A'],
        ['Account Type:', user.get_user_type_display()],
        ['Member Since:', user.date_joined.strftime('%B %d, %Y') if user.date_joined else 'N/A'],
        ['Last Login:', user.last_login.strftime('%B %d, %Y %H:%M') if user.last_login else 'N/A'],
    ]
    
    profile_table = Table(profile_data, colWidths=[2*inch, 4.5*inch])
    profile_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(profile_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Supplier-specific information
    if user.user_type == 'supplier':
        try:
            supplier = Supplier.objects.get(user=user)
            story.append(Paragraph("SUPPLIER DETAILS", heading_style))
            supplier_data = [
                ['Company Name:', supplier.company_name or 'N/A'],
                ['Location:', supplier.location or 'N/A'],
                ['Contact Number:', supplier.contact_number or 'N/A'],
                ['Consultation Fee:', f"KSH {supplier.consultation_fee}" if supplier.consultation_fee else 'N/A'],
            ]
            supplier_table = Table(supplier_data, colWidths=[2*inch, 4.5*inch])
            supplier_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f0f8ff')]),
                ('PADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(supplier_table)
            story.append(Spacer(1, 0.3*inch))
        except Supplier.DoesNotExist:
            pass
    
    # Consultant-specific information
    if user.user_type == 'consultant':
        from apps.consultations.models import ConsultantApplication
        try:
            application = ConsultantApplication.objects.filter(email=user.email).first()
            if application:
                story.append(Paragraph("CONSULTANT DETAILS", heading_style))
                consultant_data = [
                    ['Full Name:', application.full_name],
                    ['Email:', application.email],
                    ['Phone:', application.phone or 'N/A'],
                    ['Specialization:', application.specialization or 'N/A'],
                    ['Experience (Years):', str(application.experience_years)],
                    ['Consultation Rate:', f"KSH {application.consultation_rate}/hour" if application.consultation_rate else 'N/A'],
                    ['Application Status:', 'Approved' if application.processed and not application.rejected else ('Rejected' if application.rejected else 'Pending')],
                ]
                consultant_table = Table(consultant_data, colWidths=[2*inch, 4.5*inch])
                consultant_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f8e8')),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
                    ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
                    ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f0fff0')]),
                    ('PADDING', (0, 0), (-1, -1), 8),
                ]))
                story.append(consultant_table)
                story.append(Spacer(1, 0.3*inch))
        except Exception:
            pass
    
    # ==================== PAGE 2: ORDERS ====================
    story.append(PageBreak())
    story.append(Paragraph("ORDERS HISTORY", heading_style))
    
    # Get orders based on user type
    if user.user_type == 'supplier':
        # For suppliers, show orders for their products
        orders = Order.objects.filter(
            product__supplier__user=user
        ).select_related('product', 'customer').order_by('-created_at')[:20]
    else:
        # For customers and others, show their orders
        orders = Order.objects.filter(customer=user).select_related('product').order_by('-created_at')[:20]
    
    if orders:
        # Orders table header
        order_header = [['Order #', 'Product', 'Qty', 'Status', 'Total (KSH)', 'Date']]
        order_table = Table(order_header, colWidths=[1.2*inch, 2*inch, 0.5*inch, 1*inch, 1*inch, 1*inch])
        order_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff7f31')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(order_table)
        
        # Orders data
        for order in orders:
            product_name = order.product.name if order.product else (f"Plan: {order.plan_type}" if order.plan_type else 'N/A')
            order_row = [
                order.order_number or f"ORD-{order.id:08d}",
                product_name[:25] + ('...' if len(product_name) > 25 else ''),
                str(order.quantity),
                order.get_status_display(),
                f"{order.total_cost:.2f}",
                order.created_at.strftime('%Y-%m-%d'),
            ]
            order_table = Table([order_row], colWidths=[1.2*inch, 2*inch, 0.5*inch, 1*inch, 1*inch, 1*inch])
            order_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
                ('PADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(order_table)
    else:
        story.append(Paragraph("No orders found.", normal_style))
    
    story.append(Spacer(1, 0.3*inch))
    
    # ==================== PAGE 3: PRODUCTS (for suppliers) ====================
    if user.user_type == 'supplier':
        story.append(PageBreak())
        story.append(Paragraph("MY PRODUCTS", heading_style))
        
        try:
            supplier = Supplier.objects.get(user=user)
            products = Product.objects.filter(supplier=supplier).order_by('-created_at')[:20]
            
            if products:
                product_header = [['#', 'Product Name', 'Category', 'Cost (KSH)', 'Available', 'Offer']]
                product_table = Table(product_header, colWidths=[0.3*inch, 2.5*inch, 1.2*inch, 1*inch, 1*inch, 1*inch])
                product_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff7f31')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
                    ('PADDING', (0, 0), (-1, -1), 6),
                ]))
                story.append(product_table)
                
                for idx, product in enumerate(products, 1):
                    offer_display = product.get_offer_display() if product.offer else 'None'
                    product_row = [
                        str(idx),
                        product.name[:30] + ('...' if len(product.name) > 30 else ''),
                        product.get_category_display(),
                        f"{product.cost:.2f}",
                        str(product.available_quantity),
                        offer_display,
                    ]
                    product_table = Table([product_row], colWidths=[0.3*inch, 2.5*inch, 1.2*inch, 1*inch, 1*inch, 1*inch])
                    product_table.setStyle(TableStyle([
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
                        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
                        ('PADDING', (0, 0), (-1, -1), 5),
                    ]))
                    story.append(product_table)
            else:
                story.append(Paragraph("No products listed.", normal_style))
        except Supplier.DoesNotExist:
            story.append(Paragraph("Supplier profile not found.", normal_style))
        
        story.append(Spacer(1, 0.3*inch))
    
    # ==================== PAGE 4: CONSULTATIONS ====================
    story.append(PageBreak())
    story.append(Paragraph("CONSULTATIONS", heading_style))
    
    # Get consultations based on user type
    if user.user_type == 'consultant':
        consultations = Consultation.objects.filter(consultant=user).select_related('customer').order_by('-date_requested')[:20]
    else:
        consultations = Consultation.objects.filter(customer=user).select_related('consultant', 'supplier').order_by('-date_requested')[:20]
    
    if consultations:
        consult_header = [['Date', 'Consultant/Client', 'Specialization', 'Rate (KSH)', 'Status']]
        consult_table = Table(consult_header, colWidths=[1.3*inch, 2*inch, 1.5*inch, 1*inch, 1.2*inch])
        consult_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff7f31')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(consult_table)
        
        for consult in consultations:
            if user.user_type == 'consultant':
                client_name = consult.customer.get_full_name() if consult.customer else consult.customer_name or 'N/A'
            else:
                client_name = consult.consultant_name or (consult.consultant.get_full_name() if consult.consultant else 'N/A')
            
            consult_row = [
                consult.date_requested.strftime('%Y-%m-%d') if consult.date_requested else 'N/A',
                client_name[:25] + ('...' if len(client_name) > 25 else ''),
                consult.specialization[:20] + ('...' if len(consult.specialization) > 20 else '') if consult.specialization else 'N/A',
                f"{consult.consultation_rate:.2f}" if consult.consultation_rate else 'N/A',
                consult.get_status_display(),
            ]
            consult_table = Table([consult_row], colWidths=[1.3*inch, 2*inch, 1.5*inch, 1*inch, 1.2*inch])
            consult_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
                ('PADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(consult_table)
    else:
        story.append(Paragraph("No consultations found.", normal_style))
    
    story.append(Spacer(1, 0.3*inch))
    
    # ==================== PAGE 5: PLAN PURCHASES ====================
    story.append(PageBreak())
    story.append(Paragraph("PLAN PURCHASES", heading_style))
    
    plan_purchases = PlanPurchase.objects.filter(customer=user).select_related('plan').order_by('-created_at')[:20]
    
    if plan_purchases:
        plan_header = [['Purchase #', 'Plan Name', 'Amount (KSH)', 'Status', 'Date']]
        plan_table = Table(plan_header, colWidths=[1.5*inch, 2.5*inch, 1.2*inch, 1*inch, 1.3*inch])
        plan_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff7f31')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(plan_table)
        
        for purchase in plan_purchases:
            plan_row = [
                purchase.purchase_number or f"PLAN-{purchase.id:08d}",
                purchase.plan.name[:30] + ('...' if len(purchase.plan.name) > 30 else '') if purchase.plan else 'N/A',
                f"{purchase.amount:.2f}",
                purchase.get_status_display(),
                purchase.created_at.strftime('%Y-%m-%d') if purchase.created_at else 'N/A',
            ]
            plan_table = Table([plan_row], colWidths=[1.5*inch, 2.5*inch, 1.2*inch, 1*inch, 1.3*inch])
            plan_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
                ('PADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(plan_table)
    else:
        story.append(Paragraph("No plan purchases found.", normal_style))
    
    story.append(Spacer(1, 0.3*inch))
    
    # ==================== PAGE 6: CART ====================
    if user.user_type != 'supplier':
        story.append(PageBreak())
        story.append(Paragraph("SHOPPING CART", heading_style))
        
        cart_items = Cart.objects.filter(user=user).select_related('product', 'product__supplier').order_by('-added_at')[:20]
        
        if cart_items:
            cart_header = [['Product', 'Supplier', 'Qty', 'Unit Cost (KSH)', 'Total (KSH)']]
            cart_table = Table(cart_header, colWidths=[2.5*inch, 1.5*inch, 0.6*inch, 1.2*inch, 1.2*inch])
            cart_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff7f31')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(cart_table)
            
            cart_total = 0
            for item in cart_items:
                supplier_name = item.product.supplier.company_name[:20] if item.product.supplier else 'N/A'
                item_total = item.total_cost
                cart_total += item_total
                
                cart_row = [
                    item.product.name[:30] + ('...' if len(item.product.name) > 30 else ''),
                    supplier_name,
                    str(item.quantity),
                    f"{item.product.cost:.2f}",
                    f"{item_total:.2f}",
                ]
                cart_table = Table([cart_row], colWidths=[2.5*inch, 1.5*inch, 0.6*inch, 1.2*inch, 1.2*inch])
                cart_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
                    ('PADDING', (0, 0), (-1, -1), 5),
                ]))
                story.append(cart_table)
            
            # Cart total
            story.append(Spacer(1, 0.2*inch))
            total_data = [['Cart Total:', f"KSH {cart_total:.2f}"]]
            total_table = Table(total_data, colWidths=[4*inch, 2*inch])
            total_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#ff7f31')),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('PADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(total_table)
        else:
            story.append(Paragraph("Your cart is empty.", normal_style))
        
        story.append(Spacer(1, 0.3*inch))
    
    # ==================== PAGE 7: CONTACT MESSAGES ====================
    story.append(PageBreak())
    story.append(Paragraph("CONTACT MESSAGES", heading_style))
    
    messages = ContactMessage.objects.filter(email=user.email).order_by('-submitted_at')[:20]
    
    if messages:
        msg_header = [['Date', 'Subject', 'Status']]
        msg_table = Table(msg_header, colWidths=[1.5*inch, 3.5*inch, 1.5*inch])
        msg_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff7f31')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(msg_table)
        
        for msg in messages:
            status = 'Replied' if msg.is_replied else ('Read' if msg.is_read else 'Unread')
            msg_row = [
                msg.submitted_at.strftime('%Y-%m-%d') if msg.submitted_at else 'N/A',
                msg.subject[:45] + ('...' if len(msg.subject) > 45 else '') if msg.subject else 'No subject',
                status,
            ]
            msg_table = Table([msg_row], colWidths=[1.5*inch, 3.5*inch, 1.5*inch])
            msg_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
                ('PADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(msg_table)
    else:
        story.append(Paragraph("No contact messages found.", normal_style))
    
    # ==================== FOOTER ====================
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(
        f"Profile Report Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#999999'), alignment=1)
    ))
    story.append(Paragraph(
        "Smart Construction Hub - Your Trusted Construction Partner",
        ParagraphStyle('Footer2', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#999999'), alignment=1)
    ))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_order_receipt_pdf_supplier(order):
    """
    Generate an order receipt PDF for the supplier.
    
    Args:
        order: Order instance
    
    Returns:
        BytesIO object containing the PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Create styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#ff7f31'),
        spaceAfter=12,
        alignment=1
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        spaceAfter=8,
        spaceBefore=12
    )
    
    # Build story
    story = []
    
    # Header
    story.append(Paragraph("ORDER RECEIPT - SUPPLIER COPY", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Order info
    order_data = [
        ['Order Number:', order.order_number],
        ['Order Date:', order.created_at.strftime('%Y-%m-%d %H:%M:%S')],
        ['Status:', order.get_status_display()],
    ]
    order_table = Table(order_data, colWidths=[2*inch, 4.5*inch])
    order_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(order_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Customer Information
    story.append(Paragraph("CUSTOMER INFORMATION", heading_style))
    customer_data = [
        ['Customer Name:', order.customer_name or (order.customer.get_full_name() if order.customer else 'N/A')],
        ['Phone Number:', order.customer_number or (order.customer.phone if hasattr(order.customer, 'phone') else 'N/A')],
        ['Location:', order.customer_location or 'Not specified'],
    ]
    customer_table = Table(customer_data, colWidths=[2*inch, 4.5*inch])
    customer_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(customer_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Product Information
    story.append(Paragraph("PRODUCT INFORMATION", heading_style))
    product_data = [
        ['Product Name:', order.product.name],
        ['Quantity:', str(order.quantity)],
        ['Unit Cost:', f"${order.product.cost:.2f}"],
        ['Total Cost:', f"${order.total_cost:.2f}"],
    ]
    product_table = Table(product_data, colWidths=[2*inch, 4.5*inch])
    product_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(product_table)
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph(
        f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#999999'), alignment=1)
    ))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_order_receipt_pdf_customer(order):
    """
    Generate an order receipt PDF for the customer.

    Args:
        order: Order instance

    Returns:
        BytesIO object containing the PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)

    # Create styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#ff7f31'),
        spaceAfter=12,
        alignment=1
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        spaceAfter=8,
        spaceBefore=12
    )

    # Build story
    story = []

    # Header
    story.append(Paragraph("ORDER RECEIPT - CUSTOMER COPY", title_style))
    story.append(Spacer(1, 0.2*inch))

    # Order info
    order_data = [
        ['Order Number:', order.order_number],
        ['Order Date:', order.created_at.strftime('%Y-%m-%d %H:%M:%S')],
        ['Status:', order.get_status_display()],
    ]
    order_table = Table(order_data, colWidths=[2*inch, 4.5*inch])
    order_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(order_table)
    story.append(Spacer(1, 0.2*inch))

    # Supplier Information
    story.append(Paragraph("SUPPLIER INFORMATION", heading_style))
    supplier = order.product.supplier
    supplier_data = [
        ['Supplier Name:', supplier.company_name],
        ['Phone Number:', supplier.user.phone if hasattr(supplier.user, 'phone') else 'N/A'],
        ['Email:', supplier.user.email],
    ]
    supplier_table = Table(supplier_data, colWidths=[2*inch, 4.5*inch])
    supplier_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(supplier_table)
    story.append(Spacer(1, 0.2*inch))

    # Product Information
    story.append(Paragraph("PRODUCT INFORMATION", heading_style))
    product_data = [
        ['Product Name:', order.product.name],
        ['Quantity:', str(order.quantity)],
        ['Unit Cost:', f"${order.product.cost:.2f}"],
        ['Total Cost:', f"${order.total_cost:.2f}"],
    ]
    product_table = Table(product_data, colWidths=[2*inch, 4.5*inch])
    product_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(product_table)
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph(
        f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#999999'), alignment=1)
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_qualification_form_pdf():
    """
    Generate a consultant qualification form PDF with the requirements.
    
    Returns:
        BytesIO object containing the PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Create styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#ff7f31'),
        spaceAfter=12,
        alignment=1  # center
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        spaceAfter=8,
        spaceBefore=12
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6
    )
    requirement_style = ParagraphStyle(
        'Requirement',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12,
        leftIndent=20
    )
    bold_style = ParagraphStyle(
        'BoldNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6
    )
    
    # Build story
    story = []
    
    # Header
    story.append(Paragraph("CONSULTANT QUALIFICATION FORM", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Introduction
    story.append(Paragraph("Thank you for your interest in becoming a consultant with Construction Hub. Please review the qualification requirements below before submitting your application.", normal_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Requirements Section
    story.append(Paragraph("QUALIFICATION REQUIREMENTS", heading_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Requirement 1 - Education
    story.append(Paragraph("✓", ParagraphStyle('Check', parent=styles['Normal'], fontSize=12, textColor=colors.HexColor('#28a745'), spaceAfter=6)))
    story.append(Paragraph("<b>Education Qualification</b>", bold_style))
    story.append(Paragraph("Must have one of the following:", normal_style))
    story.append(Paragraph("• A degree or diploma in Construction Management", requirement_style))
    story.append(Paragraph("• A degree or diploma in Architecture", requirement_style))
    story.append(Paragraph("• A degree or diploma in Civil Engineering", requirement_style))
    story.append(Paragraph("• A degree or diploma in Building Economics", requirement_style))
    story.append(Paragraph("• Any relevant degree or diploma in construction/building related field", requirement_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Requirement 2 - Experience
    story.append(Paragraph("✓", ParagraphStyle('Check', parent=styles['Normal'], fontSize=12, textColor=colors.HexColor('#28a745'), spaceAfter=6)))
    story.append(Paragraph("<b>Work Experience</b>", bold_style))
    story.append(Paragraph("Must have 2 or more years of experience in the construction industry.", normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Requirement 3 - Communication Skills
    story.append(Paragraph("✓", ParagraphStyle('Check', parent=styles['Normal'], fontSize=12, textColor=colors.HexColor('#28a745'), spaceAfter=6)))
    story.append(Paragraph("<b>Good Communication Skills</b>", bold_style))
    story.append(Paragraph("Must possess excellent verbal and written communication skills.", normal_style))
    story.append(Paragraph("• Ability to clearly articulate ideas and technical concepts", requirement_style))
    story.append(Paragraph("• Strong interpersonal skills for client interactions", requirement_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Requirement 4 - Professional Skills
    story.append(Paragraph("✓", ParagraphStyle('Check', parent=styles['Normal'], fontSize=12, textColor=colors.HexColor('#28a745'), spaceAfter=6)))
    story.append(Paragraph("<b>Professional Skills</b>", bold_style))
    story.append(Paragraph("The following skills are required:", normal_style))
    story.append(Paragraph("• Project management and planning abilities", requirement_style))
    story.append(Paragraph("• Problem-solving and analytical skills", requirement_style))
    story.append(Paragraph("• Knowledge of construction regulations and standards", requirement_style))
    story.append(Paragraph("• Computer literacy and proficiency in relevant software", requirement_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Required Documents Section
    story.append(Paragraph("REQUIRED DOCUMENTS", heading_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("When submitting your application, please prepare the following documents:", normal_style))
    story.append(Paragraph("• Updated Resume/CV", requirement_style))
    story.append(Paragraph("• Cover Letter explaining your experience", requirement_style))
    story.append(Paragraph("• Copies of educational certificates and transcripts", requirement_style))
    story.append(Paragraph("• Work experience letters or reference letters", requirement_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Application Process Section
    story.append(Paragraph("APPLICATION PROCESS", heading_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("1. Complete the online application form", normal_style))
    story.append(Paragraph("2. Upload your resume/CV and required documents", normal_style))
    story.append(Paragraph("3. Our team will review your application", normal_style))
    story.append(Paragraph("4. If qualified, you will be contacted for an interview", normal_style))
    story.append(Paragraph("5. Upon approval, you will receive access to your consultant dashboard", normal_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Contact Information
    story.append(Paragraph("CONTACT INFORMATION", heading_style))
    story.append(Spacer(1, 0.1*inch))
    
    contact_data = [
        ['Email:', 'info@constructionhub.co.ke'],
        ['Phone:', '+254 700 000 000'],
        ['Website:', 'www.constructionhub.co.ke'],
    ]
    contact_table = Table(contact_data, colWidths=[2*inch, 4.5*inch])
    contact_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(contact_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Footer
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#999999'), alignment=1)
    ))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_plan_receipt_pdf(plan_name, plan_price, customer_name, customer_email):
    """
    Generate a plan purchase receipt PDF.

    Args:
        plan_name: Name of the purchased plan
        plan_price: Price of the plan
        customer_name: Name of the customer
        customer_email: Email of the customer

    Returns:
        BytesIO object containing the PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)

    # Create styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#ff7f31'),
        spaceAfter=12,
        alignment=1
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        spaceAfter=8,
        spaceBefore=12
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6
    )

    # Build story
    story = []

    # Header
    story.append(Paragraph("PLAN PURCHASE RECEIPT", title_style))
    story.append(Spacer(1, 0.2*inch))

    # Receipt info table
    receipt_data = [
        ['Receipt Number:', f'PLAN-{datetime.now().strftime("%Y%m%d%H%M%S")}'],
        ['Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
    ]
    receipt_table = Table(receipt_data, colWidths=[2*inch, 4.5*inch])
    receipt_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(receipt_table)
    story.append(Spacer(1, 0.2*inch))

    # Customer Information
    story.append(Paragraph("CUSTOMER INFORMATION", heading_style))
    customer_data = [
        ['Customer Name:', customer_name],
        ['Email:', customer_email],
    ]
    customer_table = Table(customer_data, colWidths=[2*inch, 4.5*inch])
    customer_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(customer_table)
    story.append(Spacer(1, 0.2*inch))

    # Plan Information
    story.append(Paragraph("PLAN INFORMATION", heading_style))
    plan_data = [
        ['Plan Name:', plan_name],
        ['Price:', f'KSH {plan_price}'],
    ]
    plan_table = Table(plan_data, colWidths=[2*inch, 4.5*inch])
    plan_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(plan_table)
    story.append(Spacer(1, 0.2*inch))

    # Planner Information
    story.append(Paragraph("PLANNER INFORMATION", heading_style))
    planner_data = [
        ['Planner Name:', 'Victor Munene'],
        ['Phone Number:', '0724689824'],
        ['Email:', 'victorjunior@gmail.com'],
    ]
    planner_table = Table(planner_data, colWidths=[2*inch, 4.5*inch])
    planner_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(planner_table)
    story.append(Spacer(1, 0.3*inch))

    # Footer
    story.append(Paragraph(
        f"Thank you for your purchase! For any inquiries, please contact the planner.",
        normal_style
    ))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#999999'), alignment=1)
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer
