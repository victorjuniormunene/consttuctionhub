#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from apps.suppliers.models import Supplier
from apps.products.models import Product
from apps.orders.models import Order

print("\n" + "="*80)
print("REMOVING SPECIFIC PRODUCTS FROM DATABASE")
print("="*80)

# Products to remove
products_to_remove = [
    # From klain12 (supplier3)
    ('klain12', 'Electrical Switches Single Gang'),
    ('klain12', 'Electrical Junction Boxes'),
    ('klain12', 'Light Fixtures LED 100W'),
    ('klain12', 'Plumbing Pipes PVC'),
    ('klain12', 'Door Frame'),

    # From mune1 (supplier4)
    ('mune1', 'PVC Pipes 4 inches (Per 6m)'),
    ('mune1', 'Bathroom Fittings Set'),
    ('mune1', 'Water Tanks (1000L)'),

    # From munene2 (supplier2)
    ('munene2', 'Electrical Wires'),

    # From Applicant One (consultant applicant)
    ('Applicant One', 'Test Product for Supplier'),

    # From Sample Supplier
    ('Sample Supplier', 'Construction Team'),
]

print("\n🗑️ Removing Products...")
removed_count = 0

for supplier_username, product_name in products_to_remove:
    try:
        supplier = Supplier.objects.get(company_name=supplier_username)
        product = Product.objects.get(supplier=supplier, name=product_name)

        # Delete associated orders first
        orders_deleted = Order.objects.filter(product=product).delete()
        print(f"  ✓ Deleted {orders_deleted[0]} orders for {product_name}")

        # Delete the product
        product.delete()
        print(f"  ✓ Removed: {product_name} by {supplier_username}")
        removed_count += 1

    except Supplier.DoesNotExist:
        print(f"  ❌ Supplier {supplier_username} not found")
    except Product.DoesNotExist:
        print(f"  ❌ Product '{product_name}' by {supplier_username} not found")

print(f"\n✅ Removed {removed_count} products from database")
print(f"📊 Remaining Products: {Product.objects.count()}")
print(f"📊 Remaining Orders: {Order.objects.count()}")

print("\n" + "="*80)
print("PRODUCT REMOVAL COMPLETED!")
print("="*80 + "\n")
