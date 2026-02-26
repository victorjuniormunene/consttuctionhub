from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.db.models import Q
from datetime import datetime
from .models import Product
from .forms import ProductForm
from apps.orders.models import Order, Cart
from apps.orders.forms import OrderForm
from apps.orders.mpesa_utils import initiate_mpesa_payment, mpesa_service

def product_list(request):
    products = Product.objects.all()

    # Handle sorting
    sort_by = request.GET.get('sort', 'name')  # Default to name
    if sort_by == 'name':
        products = products.order_by('name')
    elif sort_by == 'price-low':
        products = products.order_by('cost')
    elif sort_by == 'price-high':
        products = products.order_by('-cost')
    elif sort_by == 'newest':
        products = products.order_by('-id')  # Assuming higher id = newer

    # Handle search
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(supplier__company_name__icontains=search_query)
        )

    # Handle category filter
    category = request.GET.get('category', '')
    if category:
        products = products.filter(category=category)

    # Handle add to cart - only for authenticated customers
    if request.method == 'POST' and 'add_to_cart' in request.POST:
        if not request.user.is_authenticated or getattr(request.user, 'user_type', None) != 'customer':
            messages.error(request, 'Only logged-in customers can add items to cart.')
            return redirect('accounts:login')

        product_id = request.POST.get('product_id')
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
                quantity = int(request.POST.get('quantity', 1))

                cart_item, created = Cart.objects.get_or_create(
                    user=request.user,
                    product=product,
                    defaults={'quantity': quantity}
                )
                if not created:
                    cart_item.quantity += quantity
                    cart_item.save()

                messages.success(request, f'Added {quantity} x {product.name} to your cart.')
                return redirect('products:cart')
            except Product.DoesNotExist:
                messages.error(request, 'Product not found.')
        else:
            messages.error(request, 'Product not selected.')

    # Handle order creation - only for authenticated customers
    if request.method == 'POST' and 'create_order' in request.POST:
        if not request.user.is_authenticated or getattr(request.user, 'user_type', None) != 'customer':
            messages.error(request, 'Only logged-in customers can place orders.')
            return redirect('products:product_list')

        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            product_id = request.POST.get('product_id')
            if product_id:
                try:
                    product = Product.objects.get(id=product_id)
                    order.product = product
                    order.customer = request.user
                    order.status = 'pending_payment'  # Set status to pending payment
                    order.save()

                    # Initiate M-Pesa payment if phone number provided
                    customer_number = request.POST.get('customer_number')
                    if customer_number:
                        from apps.orders.mpesa_utils import initiate_mpesa_payment
                        payment_result = initiate_mpesa_payment(order, customer_number)
                        if payment_result.get('success'):
                            messages.success(request, f'Order #{order.order_number} created and payment initiated successfully! Total: KSH {order.total_cost}')
                            return redirect('orders:payment', order_id=order.id)
                        else:
                            messages.warning(request, f'Order #{order.order_number} created successfully, but payment initiation failed. Please contact support.')
                            return redirect('orders:payment', order_id=order.id)
                    else:
                        messages.success(request, f'Order #{order.order_number} created successfully! Total: KSH {order.total_cost}')
                        return redirect('orders:payment', order_id=order.id)

                    # Redirect to payment page
                    return redirect('orders:payment', order_id=order.id)
                except Product.DoesNotExist:
                    messages.error(request, 'Product not found.')
            else:
                messages.error(request, 'Product not selected.')
        else:
            messages.error(request, 'Please fill in all required fields.')
    else:
        form = OrderForm()

    context = {
        'products': products,
        'form': form,
        'current_sort': sort_by,
        'search_query': search_query,
        'current_category': category,
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Handle add to cart - only for authenticated customers
    if request.method == 'POST' and 'add_to_cart' in request.POST:
        if not request.user.is_authenticated or getattr(request.user, 'user_type', None) != 'customer':
            messages.error(request, 'Only logged-in customers can add items to cart.')
            return redirect('accounts:login')

        quantity = int(request.POST.get('quantity', 1))

        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        messages.success(request, f'Added {quantity} x {product.name} to your cart.')
        return redirect('products:product_detail', product_id=product.id)

    # Handle order creation - only for authenticated customers
    if request.method == 'POST' and 'create_order' in request.POST:
        if not request.user.is_authenticated or getattr(request.user, 'user_type', None) != 'customer':
            messages.error(request, 'Only logged-in customers can place orders.')
            return redirect('products:product_detail', product_id=product_id)

        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.product = product
            order.customer = request.user
            order.status = 'pending_payment'  # Set status to pending payment
            order.save()

            # Initiate M-Pesa payment if phone number provided
            customer_number = request.POST.get('customer_number')
            if customer_number:
                from apps.orders.mpesa_utils import initiate_mpesa_payment
                payment_result = initiate_mpesa_payment(order, customer_number)
                if payment_result.get('success'):
                    messages.success(request, f'Order #{order.order_number} created and payment initiated successfully! Total: KSH {order.total_cost}')
                    return redirect('orders:payment', order_id=order.id)
                else:
                    messages.warning(request, f'Order #{order.order_number} created successfully, but payment initiation failed. Please contact support.')
                    return redirect('orders:payment', order_id=order.id)
            else:
                messages.success(request, f'Order #{order.order_number} created successfully! Total: KSH {order.total_cost}')
                return redirect('orders:payment', order_id=order.id)
        else:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('products:product_detail', product_id=product_id)

    # Get all orders for this specific product, including supplier-created orders
    orders = Order.objects.filter(product=product).order_by('-created_at')
    return render(request, 'products/product_detail.html', {'product': product, 'orders': orders})

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('product_list'))
    else:
        form = ProductForm()
    return render(request, 'products/product_form.html', {'form': form})

def product_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('product_detail', args=[product.id]))
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/product_form.html', {'form': form})

def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        return HttpResponseRedirect(reverse('product_list'))
    return render(request, 'products/product_confirm_delete.html', {'product': product})

def add_to_cart(request, product_id):
    if not request.user.is_authenticated or getattr(request.user, 'user_type', None) != 'customer':
        messages.error(request, 'Only logged-in customers can add items to cart.')
        return redirect('accounts:login')

    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    # Get or create cart item
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    messages.success(request, f'Added {quantity} x {product.name} to your cart.')
    return redirect('products:product_detail', product_id=product.id)

def cart(request):
    if not request.user.is_authenticated or getattr(request.user, 'user_type', None) != 'customer':
        messages.error(request, 'Only logged-in customers can view their cart.')
        return redirect('accounts:login')

    cart_items = Cart.objects.filter(user=request.user).select_related('product__supplier')
    total_cost = sum(item.total_cost for item in cart_items)

    return render(request, 'products/cart.html', {
        'cart_items': cart_items,
        'total_cost': total_cost
    })

def remove_from_cart(request, cart_item_id):
    if not request.user.is_authenticated or getattr(request.user, 'user_type', None) != 'customer':
        messages.error(request, 'Only logged-in customers can modify their cart.')
        return redirect('accounts:login')

    cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
    cart_item.delete()

    messages.success(request, f'Removed {cart_item.product.name} from your cart.')
    return redirect('products:cart')



def checkout(request):
    if not request.user.is_authenticated or getattr(request.user, 'user_type', None) != 'customer':
        messages.error(request, 'Only logged-in customers can checkout.')
        return redirect('accounts:login')

    if request.method == 'POST':
        cart_items = Cart.objects.filter(user=request.user).select_related('product__supplier')
        if not cart_items:
            messages.error(request, 'Your cart is empty.')
            return redirect('products:cart')

        customer_name = request.POST.get('customer_name')
        customer_number = request.POST.get('customer_number')
        customer_location = request.POST.get('customer_location')

        if not all([customer_name, customer_number, customer_location]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('products:checkout')

        # Create orders for each cart item
        created_orders = []
        total_amount = 0

        for cart_item in cart_items:
            # Automatically apply the product's offer if it has one
            product_offer = cart_item.product.offer if cart_item.product else None
            
            order = Order.objects.create(
                customer=request.user,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.cost,
                customer_name=customer_name,
                customer_number=customer_number,
                customer_location=customer_location,
                status='pending_payment',  # Set status to pending payment
                offer=product_offer  # Automatically apply the product's offer
            )
            created_orders.append(order)
            total_amount += order.total_cost

        # Initiate bulk M-Pesa payment
        from apps.orders.mpesa_utils import initiate_bulk_mpesa_payment
        payment_result = initiate_bulk_mpesa_payment(created_orders, customer_number)

        if payment_result.get('success'):
            # Clear the cart after successful order creation and payment initiation
            cart_items.delete()
            messages.success(request, f'Orders created and payment initiated successfully! Total: KSH {total_amount}. Please check your phone and enter your M-Pesa PIN to complete the payment.')
            return redirect('accounts:dashboard')
        else:
            # Payment failed, but orders are created
            messages.warning(request, f'Orders created successfully, but payment initiation failed: {payment_result.get("error", "Unknown error")}. You can try payment again from your dashboard.')
            return redirect('accounts:dashboard')

    cart_items = Cart.objects.filter(user=request.user).select_related('product__supplier')
    total_cost = sum(item.total_cost for item in cart_items)

    return render(request, 'products/checkout.html', {
        'cart_items': cart_items,
        'total_cost': total_cost
    })


