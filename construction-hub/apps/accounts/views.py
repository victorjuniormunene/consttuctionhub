from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm
from django.conf import settings
from apps.accounts.models import Customer, CustomUser
from apps.suppliers.models import Supplier
from django.db.models import Q


def register(request):
    """Handle user registration using UserRegistrationForm."""
    # Check for role parameter in query string
    initial_role = request.GET.get('role', 'customer')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # form.save already set password and saved user
            # Ensure profile objects exist depending on user_type
            if user.user_type == 'customer':
                Customer.objects.get_or_create(user=user)
            elif user.user_type == 'supplier':
                # Supplier signals may auto-create, but ensure one exists
                Supplier.objects.get_or_create(user=user, defaults={'company_name': user.username})

            # authenticate and login
            user = authenticate(username=user.username, password=form.cleaned_data['password1'])
            if user:
                login(request, user)
            return redirect('accounts:dashboard')
    else:
        form = UserRegistrationForm(initial={'role': initial_role})
    return render(request, 'accounts/register.html', {'form': form, 'initial_role': initial_role})


def unified_login(request):
    """Unified login view with single form that redirects based on user role"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Try to find user by username or email
        user = None
        if '@' in username:
            try:
                user = CustomUser.objects.get(email=username)
            except CustomUser.DoesNotExist:
                pass
        else:
            try:
                user = CustomUser.objects.get(username=username)
            except CustomUser.DoesNotExist:
                pass

        if user and user.check_password(password) and user.is_active:
            login(request, user)
            # Redirect directly to dashboard app based on user role
            if user.user_type == 'consultant':
                return redirect('dashboard:consultant_dashboard')
            elif user.user_type == 'supplier':
                return redirect('dashboard:supplier_dashboard')
            else:  # customer or admin
                return redirect('dashboard:customer_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    form = UserLoginForm()
    
    # Get social account providers for Google/Facebook login buttons
    from allauth.socialaccount.models import SocialApp
    
    try:
        # Get social apps associated with current site
        # Use the provider's get_id() method which is the standard way
        social_apps = SocialApp.objects.filter(sites__id=settings.SITE_ID)
        providers = list(social_apps)
    except Exception as e:
        print(f"Error getting social providers: {e}")
        providers = []
    
    return render(request, 'accounts/login.html', {
        'form': form,
        'socialaccount_providers': providers
    })


def customer_login(request):
    """Customer-specific login view"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Try to find user by username or email
        user = None
        if '@' in username:
            try:
                user = CustomUser.objects.get(email=username)
            except CustomUser.DoesNotExist:
                pass
        else:
            try:
                user = CustomUser.objects.get(username=username)
            except CustomUser.DoesNotExist:
                pass

        if user and user.check_password(password) and user.is_active and user.user_type == 'customer':
            login(request, user)
            return redirect('dashboard:customer_dashboard')
        else:
            messages.error(request, 'Invalid username or password for customer login.')

    return render(request, 'accounts/customer_login.html')


def supplier_login(request):
    """Supplier-specific login view"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Try to find user by username or email
        user = None
        if '@' in username:
            try:
                user = CustomUser.objects.get(email=username)
            except CustomUser.DoesNotExist:
                pass
        else:
            try:
                user = CustomUser.objects.get(username=username)
            except CustomUser.DoesNotExist:
                pass

        if user and user.check_password(password) and user.is_active and user.user_type == 'supplier':
            login(request, user)
            return redirect('dashboard:supplier_dashboard')
        else:
            messages.error(request, 'Invalid username or password for supplier login.')

    return render(request, 'accounts/supplier_login.html')


def consultant_login(request):
    """Consultant-specific login view"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None and user.user_type == 'consultant':
            login(request, user)
            return redirect('dashboard:consultant_dashboard')
        else:
            messages.error(request, 'Invalid username or password for consultant login.')

    return render(request, 'accounts/consultant_login.html')


@login_required
def dashboard(request):
    # Render role-specific dashboards - prioritize consultants over suppliers
    user = request.user
    if user.user_type == 'consultant':
        # Redirect consultants to their dedicated dashboard
        return redirect('dashboard:consultant_dashboard')
    elif user.user_type == 'supplier':
        # Total focus on supplier dashboard for suppliers
        return redirect('dashboard:supplier_dashboard')
    else:
        # Redirect customers to their dedicated dashboard
        return redirect('dashboard:customer_dashboard')


def contact(request):
    """Contact page with form to send messages to admin via email."""
    from django.core.mail import send_mail
    from django.contrib import messages
    from .models import ContactMessage

    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject_text = request.POST.get('subject', '')
        message_text = request.POST.get('message', '')

        if name and email and message_text:
            # Save message to database
            contact_message = ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject_text,
                message=message_text
            )

            # Send email to admin
            admin_email = getattr(settings, 'ADMIN_EMAIL', 'victorjuniormunene@gmail.com')
            try:
                send_mail(
                    subject=f"New Contact Message from {name}: {subject_text}",
                    message=f"From: {name} ({email})\n\nMessage:\n{message_text}",
                    from_email=email,
                    recipient_list=[admin_email],
                    fail_silently=False,
                )
                messages.success(request, 'Your message has been sent to our admin team. Thank you!')
                return render(request, 'contact.html', {'submitted': True})
            except Exception as e:
                messages.error(request, f'Failed to send message: {str(e)}')
        else:
            messages.error(request, 'Please fill in all fields.')

    return render(request, 'contact.html')


def pricing(request):
    """Pricing page with architectural plans (KSH pricing)."""
    from apps.orders.models import Order
    from apps.accounts.models import ArchitecturalPlan

    # Fetch architectural plans from database
    db_plans = ArchitecturalPlan.objects.filter(is_active=True).order_by('plan_type')

    # Define membership plans (these are static)
    membership_plans = [
        {
            'name': 'Consultant Membership',
            'price': '2,500',
            'period': '/month',
            'description': 'Join our network of certified consultants and access premium opportunities',
            'features': [
                'Profile visibility on platform',
                'Access to consultation requests',
                'Client matching system',
                'Consultation scheduling tools',
                'Payment processing',
                'Performance analytics',
                'Priority support',
            ],
            'cta': 'Apply Now',
            'cta_link': '/accounts/consultant-application/'
        },
        {
            'name': 'Supplier Membership',
            'price': '4,000',
            'period': '/month',
            'description': 'Expand your business reach with our supplier network and premium features',
            'features': [
                'Enhanced product listings',
                'Priority in search results',
                'Bulk order management',
                'Advanced analytics dashboard',
                'Direct customer communication',
                'Marketing tools',
                'Dedicated account manager',
                '24/7 priority support',
            ],
            'cta': 'Become a Supplier',
            'cta_link': '/accounts/register/?role=supplier'
        }
    ]

    # If no plans in database, use fallback data
    if not db_plans.exists():
        # Fallback: Define default architectural plans
        base_plans = [
            {
                'plan_type': '2_bedroom',
                'name': '2 Bedroom Architectural Plan',
                'price': '20,000',
                'price_value': 20000,
                'period': '',
                'description': 'Complete architectural plan for a 2 bedroom house',
                'features': [
                    'Detailed floor plans',
                    'Elevation drawings',
                    'Section details',
                    'Material specifications',
                    'Construction guidelines',
                    'Digital format delivery',
                ],
            },
            {
                'plan_type': '3_bedroom',
                'name': '3 Bedroom Architectural Plan',
                'price': '25,000',
                'price_value': 25000,
                'period': '',
                'description': 'Comprehensive architectural plan for a 3 bedroom house',
                'features': [
                    'Detailed floor plans',
                    'Elevation drawings',
                    'Section details',
                    'Material specifications',
                    'Construction guidelines',
                    'Digital format delivery',
                    'Additional customization options',
                ],
                'featured': True
            },
        ]
    else:
        # Convert database plans to format compatible with template
        base_plans = []
        for plan in db_plans:
            plan_dict = {
                'plan_type': plan.plan_type,
                'name': plan.name,
                'price': f"{int(plan.price):,}",
                'price_value': int(plan.price),
                'period': '',
                'description': plan.description,
                'features': plan.features if plan.features else [],
            }
            # Mark 3 bedroom as featured
            if plan.plan_type == '3_bedroom':
                plan_dict['featured'] = True
            base_plans.append(plan_dict)

    # Check purchase status for architectural plans if user is authenticated
    pricing_plans = []
    if request.user.is_authenticated:
        for plan in base_plans:
            plan_copy = plan.copy()

            # Skip non-architectural plans (consultant/supplier memberships)
            if 'plan_type' not in plan:
                pricing_plans.append(plan_copy)
                continue

            # Check if user has purchased this plan
            plan_orders = Order.objects.filter(
                customer=request.user,
                plan_type=plan['plan_type']
            ).order_by('-created_at')

            if plan_orders.exists():
                latest_order = plan_orders.first()
                if latest_order.status == 'paid':
                    # User has paid - show download button
                    plan_copy['cta'] = 'Download Plan'
                    plan_copy['cta_link'] = f'/accounts/download_plan/{plan["plan_type"]}/'
                    plan_copy['status'] = 'paid'
                elif latest_order.status in ['pending_payment', 'saved']:
                    # Payment pending - show complete payment button
                    plan_copy['cta'] = 'Complete Payment'
                    plan_copy['cta_link'] = f'/accounts/complete_payment/{latest_order.id}/'
                    plan_copy['status'] = 'pending'
                else:
                    # Other status - show purchase again
                    plan_copy['cta'] = 'Purchase Now'
                    plan_copy['cta_link'] = f'/accounts/purchase_plan/{plan["plan_type"]}/'
            else:
                # No order exists - show purchase button
                plan_copy['cta'] = 'Purchase Now'
                plan_copy['cta_link'] = f'/accounts/purchase_plan/{plan["plan_type"]}/'

            pricing_plans.append(plan_copy)
    else:
        # For non-authenticated users, show purchase buttons
        for plan in base_plans:
            plan_copy = plan.copy()
            if 'plan_type' in plan:
                plan_copy['cta'] = 'Purchase Now'
                plan_copy['cta_link'] = f'/accounts/purchase_plan/{plan["plan_type"]}/'
            pricing_plans.append(plan_copy)

    # Add membership plans to the list
    pricing_plans.extend(membership_plans)

    return render(request, 'pricing.html', {'plans': pricing_plans})


def about(request):
    """About page with company information and testimonials."""
    testimonials = [
        {
            'name': 'John Smith',
            'company': 'BuildTech Contractors',
            'quote': 'Construction Hub transformed how we manage our projects. The platform is intuitive and has saved us countless hours on documentation.',
            'role': 'Project Manager'
        },
        {
            'name': 'Sarah Johnson',
            'company': 'Metropolitan Builders',
            'quote': 'Outstanding customer support and continuous improvements. This is exactly what the construction industry needed.',
            'role': 'Operations Director'
        },
        {
            'name': 'Mike Chen',
            'company': 'Premium Construction',
            'quote': 'The reporting features alone have improved our project visibility and stakeholder communication tremendously.',
            'role': 'Construction Manager'
        }
    ]
    
    return render(request, 'about.html', {'testimonials': testimonials})


def consultant_application(request):
    """Consultant application view — handle form submission and store applications."""
    from apps.suppliers.models import Supplier
    from apps.consultations.models import ConsultantApplication

    if request.method == 'POST':
        full_name = request.POST.get('full_name', request.user.get_full_name() if request.user.is_authenticated else '')
        email = request.POST.get('email', request.user.email if request.user.is_authenticated else '')
        phone = request.POST.get('phone', '')
        specialization = request.POST.get('specialization', 'General Construction')
        experience = int(request.POST.get('experience_years', '1') or 0)
        cover_letter = request.POST.get('cover_letter', '')

        # file uploads
        resume = request.FILES.get('resume')
        cv = request.FILES.get('cv')

        # Persist application
        app = ConsultantApplication.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=full_name,
            email=email,
            phone=phone,
            specialization=specialization,
            experience_years=experience,
            cover_letter=cover_letter,
            resume=resume,
            cv=cv,
        )

        # Only create/update Supplier profile if user is authenticated
        if request.user.is_authenticated:
            # Optionally create or update Supplier profile (leave to admin to approve)
            supplier, created = Supplier.objects.get_or_create(
                user=request.user,
                defaults={
                    'company_name': full_name,
                    'contact_number': phone,
                    'location': 'Available for consultation',
                    'consultation_fee': 100,
                }
            )

            if not created:
                supplier.company_name = full_name
                supplier.contact_number = phone
                supplier.save()

        print(f"Consultant application saved: {app}")
        return render(request, 'consultant_application.html', {'submitted': True, 'application': app})

    return render(request, 'consultant_application.html')


@login_required
def my_consultant_applications(request):
    """View user's consultant applications with download options."""
    from apps.consultations.models import ConsultantApplication

    applications = ConsultantApplication.objects.filter(user=request.user).order_by('-submitted_at')
    return render(request, 'consultant_applications_list.html', {'applications': applications})


@login_required
def purchase_plan(request, plan_type):
    """Create order for architectural plan and redirect to payment"""
    from apps.orders.models import Order
    from apps.products.models import Product
    from django.shortcuts import redirect
    from django.contrib import messages

    # Validate plan type
    plan_prices = {
        '2_bedroom': 20000,
        '3_bedroom': 25000
    }

    if plan_type not in plan_prices:
        messages.error(request, 'Invalid plan type.')
        return redirect('accounts:pricing')

    price = plan_prices[plan_type]

    # Check if user already has a paid order for this plan
    existing_paid_order = Order.objects.filter(
        customer=request.user,
        plan_type=plan_type,
        status='paid'
    ).exists()

    if existing_paid_order:
        messages.info(request, 'You have already purchased this plan.')
        return redirect('accounts:pricing')

    # Create a dummy product for the plan (or find existing one)
    # For now, we'll create orders without a product since these are digital plans
    order = Order.objects.create(
        customer=request.user,
        plan_type=plan_type,
        quantity=1,
        price=price,
        status='pending_payment',
        customer_name=request.user.get_full_name() or request.user.username,
        customer_number='',  # Will be filled during payment
        customer_location=''  # Will be filled during payment
    )

    # Redirect to payment page
    return redirect('orders:payment', order_id=order.id)


@login_required
def complete_payment(request, order_id):
    """Redirect to payment page for existing order"""
    from apps.orders.models import Order
    from django.shortcuts import redirect, get_object_or_404
    from django.contrib import messages

    order = get_object_or_404(Order, id=order_id, customer=request.user)

    # Check if already paid
    if order.status == 'paid':
        messages.info(request, 'This order has already been paid for.')
        return redirect('accounts:pricing')

    # Redirect to payment page
    return redirect('orders:payment', order_id=order.id)


@login_required
def download_plan(request, plan_type):
    """Download architectural plan image after payment verification"""
    from apps.orders.models import Order
    from django.http import FileResponse
    from django.contrib import messages
    import os
    from django.conf import settings

    # Check if user has paid for this plan type
    paid_orders = Order.objects.filter(
        customer=request.user,
        plan_type=plan_type,
        status='paid'
    )

    if not paid_orders.exists():
        messages.error(request, 'You have not purchased this plan or payment is not complete.')
        return redirect('accounts:pricing')

    # Map plan types to image files
    image_files = {
        '2_bedroom': '2 bedroom plan.jpg',
        '3_bedroom': '3 bedroom.jpg'
    }

    if plan_type not in image_files:
        messages.error(request, 'Invalid plan type.')
        return redirect('accounts:pricing')

    image_filename = image_files[plan_type]
    image_path = f'static/images/{image_filename}'

    try:
        # Return file as download
        file_path = os.path.join(settings.BASE_DIR, image_path)
        if os.path.exists(file_path):
            response = FileResponse(open(file_path, 'rb'), content_type='image/jpeg')
            response['Content-Disposition'] = f'attachment; filename="{image_filename}"'
            return response
        else:
            messages.error(request, 'Plan file not found. Please contact support.')
            return redirect('accounts:pricing')
    except Exception as e:
        messages.error(request, f'Error downloading file: {str(e)}')
        return redirect('accounts:pricing')


@login_required
def download_plan_receipt(request, plan_type):
    """Download plan purchase receipt PDF after payment verification"""
    from apps.orders.models import Order
    from django.http import HttpResponse
    from django.contrib import messages
    from apps.consultations.pdf_utils import generate_plan_receipt_pdf

    # Check if user has paid for this plan type
    paid_orders = Order.objects.filter(
        customer=request.user,
        plan_type=plan_type,
        status='paid'
    )

    if not paid_orders.exists():
        messages.error(request, 'You have not purchased this plan or payment is not complete.')
        return redirect('accounts:pricing')

    # Get the latest paid order
    order = paid_orders.first()

    # Map plan types to plan names and prices
    plan_details = {
        '2_bedroom': {'name': '2 Bedroom Architectural Plan', 'price': 20000},
        '3_bedroom': {'name': '3 Bedroom Architectural Plan', 'price': 25000}
    }

    if plan_type not in plan_details:
        messages.error(request, 'Invalid plan type.')
        return redirect('accounts:pricing')

    plan_name = plan_details[plan_type]['name']
    plan_price = plan_details[plan_type]['price']
    customer_name = request.user.get_full_name() or request.user.username
    customer_email = request.user.email

    try:
        # Generate PDF
        pdf_buffer = generate_plan_receipt_pdf(plan_name, plan_price, customer_name, customer_email)

        # Return PDF as download
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="plan_receipt_{plan_type}.pdf"'
        return response
    except Exception as e:
        messages.error(request, f'Error generating receipt: {str(e)}')
        return redirect('accounts:pricing')


def home(request):
    """Home page view"""
    return render(request, 'home.html')


@login_required
def send_email_to_user(request):
    """Admin view to send email to a user."""
    from django.core.mail import send_mail
    from django.http import JsonResponse
    from django.views.decorators.http import require_http_methods
    import json

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            recipient_email = data.get('email', '')
            subject = data.get('subject', '')
            message = data.get('message', '')

            if not recipient_email or not subject or not message:
                return JsonResponse({'success': False, 'error': 'All fields are required'}, status=400)

            # Get admin email for from_email
            admin_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@constructionhub.co.ke')

            # Send the email
            send_mail(
                subject=subject,
                message=message,
                from_email=admin_email,
                recipient_list=[recipient_email],
                fail_silently=False,
            )

            return JsonResponse({'success': True, 'message': f'Email sent to {recipient_email}'})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
