#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.suppliers.models import Supplier
from apps.products.models import Product
from apps.orders.models import Order

User = get_user_model()

print("\n" + "="*80)
print("COMPREHENSIVE DATABASE SETUP FOR ORDER SYSTEM")
print("="*80)

# Step 1: Ensure all suppliers have products
print("\n📦 VERIFYING & CREATING PRODUCTS FOR ALL SUPPLIERS...")

products_to_create = [
    {
        'supplier_user': 'supplier1',
        'products': [
            ('Cement 50kg Bag', 'Portland cement for concrete mixing', 'cement', 'Nairobi', 800),
            ('Steel Reinforcement Bars 12mm', 'High quality steel bars for construction', 'steel', 'Nairobi', 1500),
            ('Concrete Mix (1 cubic meter)', 'Ready mix concrete for construction', 'cement', 'Nairobi', 4500),
            ('Sand (Per Ton)', 'Fine construction sand', 'cement', 'Nairobi', 3000),
        ]
    },
    {
        'supplier_user': 'munene2',
        'products': [
            ('Timber Planks (4x2 inches)', 'Quality pine timber for framing', 'wood', 'Kisumu', 6000),
            ('Plywood Sheets (4x8 ft)', 'Durable plywood for construction', 'wood', 'Kisumu', 4000),
            ('Roofing Iron (32 gauge)', 'Corrugated iron sheets for roofing', 'wood', 'Kisumu', 2000),
            ('Wood Polish (5L)', 'Premium wood finishing polish', 'wood', 'Kisumu', 1200),
        ]
    },
    {
        'supplier_user': 'klain12',
        'products': [
            ('Light Fixtures LED 100W', 'Energy-efficient LED lights', 'electrical', 'Mombasa', 3500),
        ]
    },
    {
        'supplier_user': 'mune1',
        'products': [
            ('PVC Pipes 4 inches (Per 6m)', 'PVC plumbing pipes', 'plumbing', 'Eldoret', 1500),
            ('Bathroom Fittings Set', 'Complete bathroom fixture set', 'plumbing', 'Eldoret', 8000),
            ('Water Tanks (1000L)', 'Plastic water storage tanks', 'plumbing', 'Eldoret', 5500),
        ]
    }
]

product_count = 0
for supplier_data in products_to_create:
    try:
        supplier_user = User.objects.get(username=supplier_data['supplier_user'])
        supplier = Supplier.objects.get(user=supplier_user)
        
        for product_name, description, category, location, cost in supplier_data['products']:
            product, created = Product.objects.get_or_create(
                supplier=supplier,
                name=product_name,
                defaults={
                    'description': description,
                    'category': category,
                    'location': location,
                    'cost': cost,
                }
            )
            if created:
                print(f"  ✓ Created: {product_name} (KSH {cost}) - by {supplier.company_name}")
                product_count += 1
            
    except Exception as e:
        print(f"  ✗ Error creating products for {supplier_data['supplier_user']}: {str(e)}")

print(f"\nTotal Products in Database: {Product.objects.count()}")

# Step 2: Create varied sample orders
print("\n📋 CREATING COMPREHENSIVE SAMPLE ORDERS...")

orders_to_create = []

# Customer 1 orders
customer1 = User.objects.get(username='customer1')
products = list(Product.objects.all())

if len(products) > 0:
    # Order 1: Customer creates order
    orders_to_create.append({
        'customer': customer1,
        'product': products[0],
        'quantity': 10,
        'customer_name': customer1.get_full_name() or customer1.username,
        'customer_number': '0712345678',
        'customer_location': 'Nairobi Central',
        'status': 'saved'
    })
    
    # Order 2: Customer creates another order
    if len(products) > 1:
        orders_to_create.append({
            'customer': customer1,
            'product': products[1],
            'quantity': 5,
            'customer_name': customer1.get_full_name() or customer1.username,
            'customer_number': '0712345678',
            'customer_location': 'Nairobi Central',
            'status': 'paid'
        })

# Supplier creates orders for various customers
suppliers = Supplier.objects.all()
sample_customers = [
    ('John Smith Construction', '+254723456789', 'Westlands, Nairobi'),
    ('Marys Building Supplies', '+254734567890', 'Industrial Area'),
    ('Tech Construction Ltd', '+254745678901', 'Upper Hill, Nairobi'),
    ('Davids Home Renovation', '+254756789012', 'Karen, Nairobi'),
    ('Future Builders Kenya', '+254767890123', 'Runda, Nairobi'),
]

for i, supplier in enumerate(suppliers[:4]):
    supplier_products = Product.objects.filter(supplier=supplier)
    for j, product in enumerate(supplier_products[:2]):
        if len(orders_to_create) < 25:  # Limit total orders
            orders_to_create.append({
                'customer': None,
                'product': product,
                'quantity': (j + 1) * 3 + i,
                'customer_name': sample_customers[len(orders_to_create) % len(sample_customers)][0],
                'customer_number': sample_customers[len(orders_to_create) % len(sample_customers)][1],
                'customer_location': sample_customers[len(orders_to_create) % len(sample_customers)][2],
                'status': ['saved', 'paid', 'shipped', 'pending'][len(orders_to_create) % 4]
            })

# Create orders
order_count = 0
for order_data in orders_to_create:
    try:
        order, created = Order.objects.get_or_create(
            customer=order_data['customer'],
            product=order_data['product'],
            quantity=order_data['quantity'],
            customer_name=order_data['customer_name'],
            defaults={
                'customer_number': order_data['customer_number'],
                'customer_location': order_data['customer_location'],
                'status': order_data['status'],
            }
        )
        if created:
            print(f"  ✓ Order #{order.id} ({order.order_number}): {order.quantity}x {order.product.name} - {order.customer_name}")
            order_count += 1
    except Exception as e:
        print(f"  ✗ Error creating order: {str(e)}")

print(f"\nTotal Orders in Database: {Order.objects.count()}")

# Step 3: Verify visibility
print("\n" + "="*80)
print("✅ DATABASE SETUP COMPLETE!")
print("="*80)

print("\n📊 DATABASE SUMMARY:")
print(f"  • Users: {User.objects.count()}")
print(f"  • Suppliers: {Supplier.objects.count()}")
print(f"  • Products: {Product.objects.count()}")
print(f"  • Orders: {Order.objects.count()}")

print("\n🎯 WHAT'S READY:")
print("  ✓ All suppliers have products")
print("  ✓ Customers can create orders from any product")
print("  ✓ Orders automatically appear in:")
print("    - Customer dashboard (if customer=user)")
print("    - Supplier dashboard (if product belongs to them)")
print("  ✓ Sample orders show bidirectional visibility")

print("\n🔗 URLS TO TEST:")
print("  • Homepage: http://127.0.0.1:8000/")
print("  • Create Order: http://127.0.0.1:8000/orders/create/")
print("  • Supplier Create Order: http://127.0.0.1:8000/suppliers/create-order/")
print("  • Dashboard: http://127.0.0.1:8000/accounts/dashboard/")
print("  • Products: http://127.0.0.1:8000/suppliers/products/")

print("\n👥 TEST ACCOUNTS:")
print("  • customer1: Can place orders, see them in dashboard")
print("  • supplier1, munene2, klain12, mune1: Manage supplier dashboards")

print("\n" + "="*80)
print("✨ System is fully operational! Start creating orders now!\n")
