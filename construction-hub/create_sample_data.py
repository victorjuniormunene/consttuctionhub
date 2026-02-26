#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from apps.suppliers.models import Supplier
from apps.products.models import Product
from apps.orders.models import Order
from django.contrib.auth import get_user_model

User = get_user_model()

print("\n" + "="*80)
print("CREATING SAMPLE DATA FOR TESTING")
print("="*80)

# Get suppliers and ensure they have the correct role and contact info
supplier1 = Supplier.objects.get(user__username='supplier1')
supplier1.user.role = 'supplier'
supplier1.user.save()
supplier1.location = 'Nairobi'
supplier1.contact_number = '0712345678'
supplier1.save()

supplier2 = Supplier.objects.get(user__username='munene2')
supplier2.user.role = 'supplier'
supplier2.user.save()
supplier2.location = 'Kisumu'
supplier2.contact_number = '0723456789'
supplier2.save()

supplier3 = Supplier.objects.get(user__username='klain12')
supplier3.user.role = 'supplier'
supplier3.user.save()
supplier3.location = 'Mombasa'
supplier3.contact_number = '0734567890'
supplier3.save()

# Update the fourth supplier (mune1) - already has location and contact
supplier4 = Supplier.objects.get(user__username='mune1')
supplier4.user.role = 'supplier'
supplier4.user.save()
# mune1 already has location='embu' and contact_number='04655656565'

# Create Products for each supplier
products_data = [
    (supplier1, 'Cement 50kg', 'Portland cement for construction', 'cement', 'Nairobi', 800),
    (supplier1, 'Sand (Fine)', 'Fine construction sand', 'sand', 'Nairobi', 450),
    (supplier1, 'Steel Bars 16mm', 'High-grade steel reinforcement bars', 'steel', 'Nairobi', 1200),
    (supplier2, 'Cement 50kg', 'Premium cement for construction', 'cement', 'Kisumu', 850),
    (supplier2, 'Sand (Coarse)', 'Coarse construction sand', 'sand', 'Kisumu', 400),
    (supplier2, 'Timber (Pine)', 'Quality pine timber boards', 'wood', 'Kisumu', 5000),
    (supplier3, 'Cement 50kg', 'Economy cement for construction', 'cement', 'Mombasa', 750),
    (supplier3, 'Sand (River)', 'River sand for construction', 'sand', 'Mombasa', 500),
    (supplier3, 'Plumbing Pipes PVC', 'PVC plumbing pipes 4 inches', 'plumbing', 'Mombasa', 600),
    (supplier3, 'Door Frame', 'Wooden door frame with handle', 'wood', 'Mombasa', 3500),
]

print("\n📦 Creating Products...")
created_products = []
for supplier, name, description, category, location, cost in products_data:
    product, created = Product.objects.get_or_create(
        supplier=supplier,
        name=name,
        defaults={
            'description': description,
            'category': category,
            'location': location,
            'cost': cost,
            'image_url': '/static/images/steel reinforcement.jpg' if 'steel' in name.lower() else None,
        }
    )
    if created:
        print(f"  ✓ {name} - KSH {cost}")
    else:
        print(f"  ~ {name} already exists")
    created_products.append(product)

print(f"\nTotal Products: {Product.objects.count()}")

# Get customer users
customer1 = User.objects.get(username='customer1')
customer2 = User.objects.get(username='testcustomer')

# Create exactly 10 orders for customer1 to show in their dashboard
print("\n📋 Creating 10 Sample Orders for Customer Dashboard...")

orders_data = [
    # Order 1-5: Various products with different statuses
    (customer1, created_products[0], 5, 'saved'),      # Cement 50kg
    (customer1, created_products[1], 10, 'pending'),    # Sand (Fine)
    (customer1, created_products[2], 3, 'paid'),        # Steel Bars 16mm
    (customer1, created_products[3], 8, 'shipped'),     # Cement 50kg (supplier2)
    (customer1, created_products[4], 12, 'completed'),  # Sand (Coarse)

    # Order 6-10: More products with different statuses
    (customer1, created_products[5], 2, 'saved'),       # Timber (Pine)
    (customer1, created_products[9], 1, 'pending'),    # Door Frame
    (customer1, created_products[7], 6, 'paid'),        # Cement 50kg (supplier3)
    (customer1, created_products[8], 18, 'shipped'),    # Sand (River)
    (customer1, created_products[9], 4, 'completed'),   # Plumbing Pipes PVC
]

created_orders = []
for i, (customer, product, quantity, status) in enumerate(orders_data, 1):
    order = Order.objects.create(
        customer=customer,
        product=product,
        quantity=quantity,
        customer_name=customer.get_full_name() or customer.username,
        customer_number='0712345678',
        customer_location='Nairobi, Kenya',
        status=status,
    )
    created_orders.append(order)
    print(f"  ✓ Order #{order.id} ({order.order_number}) - {customer.username} ordered {quantity}x {product.name} - Status: {status}")

print(f"\nTotal Orders: {Order.objects.count()}")

# Create orders for all products if they don't have any
print("\n📋 Ensuring all products have at least one order...")
all_products = Product.objects.all()
for product in all_products:
    if not product.orders.exists():
        # Create a Sharon order for this product
        Order.objects.create(
            product=product,
            quantity=5,
            customer_name= 'Sharon Customer',
            customer_number='0712345678',
            customer_location='Sharon Location',
            status='saved',
        )
        print(f"  ✓ Created sample order for {product.name}")

print(f"\nFinal Total Orders: {Order.objects.count()}")

# Ensure every customer user has at least one order
print("\n📋 Ensuring every customer has at least one order...")
customer_users = User.objects.filter(role='customer')
for customer in customer_users:
    if not Order.objects.filter(customer=customer).exists():
        # Get a random product
        product = created_products[0] if created_products else Product.objects.first()
        Order.objects.create(
            customer=customer,
            product=product,
            quantity=3,
            customer_name=customer.get_full_name() or customer.username,
            customer_number='0712345678',
            customer_location='Nairobi, Kenya',
            status='saved',
        )
        print(f"  ✓ Created sample order for customer {customer.username}")

print(f"\nFinal Total Orders: {Order.objects.count()}")

print("\n" + "="*80)
print("✅ SAMPLE DATA CREATED SUCCESSFULLY!")
print("="*80)
print("\n📊 TEST SCENARIOS:")
print("\n1. Login as 'customer1':")
print("   - Should see orders #1 and #4 (they created them)")
print("   - Should see order #3 (supplier created for 'testcustomer', not matching)")
print("   - Should NOT see order #2 and #5 (no name match)")

print("\n2. Login as 'testcustomer':")
print("   - Should see order #3 (supplier created with their name)")

print("\n3. Login as 'supplier1':")
print("   - Should see orders #1 and #2 (their products)")

print("\n4. Login as 'supplier2':")
print("   - Should see orders #3 and #5 (their products)")

print("\n" + "="*80)
print("🌐 Access the application:")
print("   URL: http://127.0.0.1:8000/")
print("   Dashboard: http://127.0.0.1:8000/accounts/dashboard/")
print("="*80 + "\n")
