from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Supplier, Product as SupplierProduct
from apps.products.models import Product
from .forms import ProductForm, SupplierOrderForm
from apps.orders.forms import OrderForm
from apps.orders.models import Order
from django.contrib import messages
from django.shortcuts import HttpResponse

def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            # ensure a Supplier instance exists for this user
            supplier, _ = Supplier.objects.get_or_create(user=request.user, defaults={'company_name': request.user.username})
            product.supplier = supplier
            product.save()
            return redirect('suppliers:product_list')
    else:
        form = ProductForm()
    return render(request, 'suppliers/product_form.html', {'form': form})

@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('suppliers:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'suppliers/product_form.html', {'form': form})

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('suppliers:product_list')
    return render(request, 'suppliers/product_confirm_delete.html', {'product': product})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    supplier = product.supplier
    
    return render(request, 'products/product_detail.html', {
        'product': product,
        'supplier': supplier,
    })


@login_required
def create_order_for_supplier(request):
    """Allow a supplier to create an order for any product."""
    # ensure supplier profile
    supplier = Supplier.objects.filter(user=request.user).first()
    if not supplier:
        messages.error(request, 'You must have a supplier profile to create orders.')
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = SupplierOrderForm(request.POST, request.FILES, supplier=supplier)
        if form.is_valid():
            # Get cleaned data
            product_name = form.cleaned_data['product_name']
            quantity = form.cleaned_data['quantity']
            price = form.cleaned_data['price']
            available_quantity = form.cleaned_data['available_quantity']
            supplier_name = form.cleaned_data['supplier_name']
            supplier_phone = form.cleaned_data['supplier_phone']
            supplier_location = form.cleaned_data['supplier_location']
            product_image = form.cleaned_data.get('product_image')
            offer = form.cleaned_data.get('offer', '')  # Get the offer field

            # Update supplier information if changed
            supplier.company_name = supplier_name
            supplier.contact_number = supplier_phone
            supplier.location = supplier_location
            supplier.save()

            # Get or create the product
            product, created = Product.objects.get_or_create(
                name__iexact=product_name,
                supplier=supplier,
                defaults={
                    'name': product_name.title(),
                    'description': f'{product_name.title()} product',
                    'category': product_name.lower(),
                    'cost': price,  # Use the price from the form
                    'available_quantity': available_quantity,  # Set stock quantity
                    'location': supplier.location or 'N/A',  # Add required location field
                    'offer': offer,  # Save the offer to the product
                }
            )

            # If product already exists, update the stock quantity and offer
            if not created:
                product.available_quantity = available_quantity
                product.offer = offer  # Update the offer
                product.save()

            # Handle product image upload if provided
            if product_image:
                # Save the image to media directory
                import os
                from django.conf import settings
                from django.core.files.storage import default_storage
                from django.core.files.base import ContentFile

                # Create a unique filename
                ext = os.path.splitext(product_image.name)[1]
                filename = f"product_{product.id}_{product_name.replace(' ', '_')}{ext}"

                # Save the file
                file_path = os.path.join('product_images', filename)
                path = default_storage.save(file_path, ContentFile(product_image.read()))

                # Update product with image URL (relative path)
                product.image_url = path
                product.save()

            # Create order
            order = Order.objects.create(
                product=product,
                quantity=quantity,
                price=price,  # Set the price from the form
                ordering_supplier=request.user,  # Track which supplier created this order
                offer=offer,  # Save the offer to the order
            )

            messages.success(request, f'Order created (#{order.order_number}). Product "{product.name}" {"created" if created else "updated"}.')
            # Redirect to supplier dashboard since this is a supplier creating the order
            return redirect('dashboard:supplier_dashboard')
        else:
            messages.error(request, f'Form validation failed: {form.errors}')
    else:
        form = SupplierOrderForm(supplier=supplier)

    return render(request, 'suppliers/supplier_create_order.html', {
        'form': form,
        'supplier': supplier,
    })


@login_required
def sell_all_orders(request):
    """Mark all pending orders for this supplier as completed (sold)."""
    supplier = Supplier.objects.filter(user=request.user).first()
    if not supplier:
        messages.error(request, 'You must have a supplier profile to perform this action.')
        return redirect('accounts:dashboard')

    pending_qs = Order.objects.filter(supplier=supplier, status='pending')
    count = pending_qs.count()
    if count == 0:
        messages.info(request, 'No pending orders to sell.')
    else:
        pending_qs.update(status='completed')
        messages.success(request, f'Marked {count} order(s) as completed.')

    return redirect('accounts:dashboard')


@login_required
def order_detail(request, pk):
    """View order details for suppliers."""
    order = get_object_or_404(Order, Q(pk=pk) & (Q(product__supplier__user=request.user) | Q(ordering_supplier=request.user)))

    # Handle GET actions for status updates (from dashboard links)
    if getattr(request.user, 'is_supplier', False):
        action = request.GET.get('action')
        # Handle mark_shipped (In Transit) - works from paid, pending, or any non-completed status
        if action == 'mark_shipped' and order.status in ['pending', 'paid', 'saved', 'complete_waiting_transport']:
            order.status = 'shipped'
            order.save()
            messages.success(request, 'Order marked as in transit (shipped).')
            return redirect('dashboard:supplier_dashboard')
        # Handle mark_complete - works from any status except already completed
        elif action == 'mark_complete' and order.status != 'completed':
            order.status = 'completed'
            order.save()
            # Send completion email to customer
            try:
                from apps.orders.views import send_order_completion_email_to_customer
                send_order_completion_email_to_customer(order)
            except Exception as e:
                print(f"Failed to send order completion email: {str(e)}")
            messages.success(request, 'Order marked as completed.')
            return redirect('dashboard:supplier_dashboard')

    return render(request, 'orders/order_detail.html', {'order': order})
