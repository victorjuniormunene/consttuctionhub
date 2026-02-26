#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.products.models import Product
from apps.suppliers.models import Supplier
from apps.orders.models import Order
from django.db.models import Q

User = get_user_model()

print("\n" + "="*80)
print("TESTING ORDER FLOW - VERIFY BIDIRECTIONAL VISIBILITY")
print("="*80)

# Get a customer and supplier
customer = User.objects.get(username='customer1')
supplier = Supplier.objects.get(user__username='supplier1')

# Get their product
product = Product.objects.filter(supplier=supplier).first()

if not product:
    print("\n❌ ERROR: Supplier has no products!")
else:
    print(f"\n✓ Found Product: {product.name} by {supplier.company_name}")
    
    # Create a test order
    print("\n📝 Creating test order...")
    test_order = Order.objects.create(
        customer=customer,
        product=product,
        quantity=5,
        customer_name=customer.get_full_name() or customer.username,
        customer_number='0712345678',
        customer_location='Test Location',
        status='saved'
    )
    print(f"✓ Order created: #{test_order.id} ({test_order.order_number})")
    
    # Check if order appears in CUSTOMER dashboard
    print("\n📊 CUSTOMER DASHBOARD CHECK:")
    customer_full_name = customer.get_full_name() or customer.username
    customer_orders = Order.objects.filter(
        Q(customer=customer) |
        Q(customer__isnull=True, customer_name=customer_full_name)
    )
    
    if test_order in customer_orders:
        print(f"✅ Order FOUND in customer dashboard ({customer_orders.count()} total)")
    else:
        print(f"❌ Order NOT FOUND in customer dashboard")
    
    # Check if order appears in SUPPLIER dashboard
    print("\n🏢 SUPPLIER DASHBOARD CHECK:")
    supplier_orders = Order.objects.filter(product__supplier=supplier)
    
    if test_order in supplier_orders:
        print(f"✅ Order FOUND in supplier dashboard ({supplier_orders.count()} total)")
    else:
        print(f"❌ Order NOT FOUND in supplier dashboard")
    
    # Show all orders for verification
    print("\n📋 ALL ORDERS IN DATABASE:")
    all_orders = Order.objects.all().order_by('-id')[:10]
    for o in all_orders:
        customer_info = o.customer.username if o.customer else f"(No user - name: {o.customer_name})"
        print(f"  Order #{o.id} ({o.order_number}): {o.quantity}x {o.product.name} - Customer: {customer_info} - Status: {o.status}")
    
    print("\n" + "="*80)
    if test_order in customer_orders and test_order in supplier_orders:
        print("✅ SUCCESS! Order appears on BOTH sides!")
    else:
        print("❌ ISSUE: Order not showing on both sides")
    print("="*80 + "\n")
