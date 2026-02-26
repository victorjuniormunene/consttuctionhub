#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from apps.suppliers.models import Supplier
from apps.products.models import Product

print("\n" + "="*80)
print("ADDING BACK TEST PRODUCT")
print("="*80)

try:
    # Get the Applicant One supplier
    supplier = Supplier.objects.get(user__username='Applicant One')

    # Create the test product
    product, created = Product.objects.get_or_create(
        supplier=supplier,
        name='Door Frame Test Product',
        defaults={
            'description': 'Wooden door frame with handle - auto-created test product',
            'category': 'wood',
            'location': 'Test Location',
            'cost': 99.99,
        }
    )

    if created:
        print("  ✓ Test product created successfully")
    else:
        print("  ~ Test product already exists")

    print(f"Product: {product.name}")
    print(f"Supplier: {product.supplier.company_name}")
    print(f"Cost: KSH {product.cost}")
    print(f"Category: {product.get_category_display()}")

except Supplier.DoesNotExist:
    print("  ❌ Supplier 'Applicant One' not found")
except Exception as e:
    print(f"  ❌ Error: {e}")

print("\n" + "="*80)
print("TEST PRODUCT ADDITION COMPLETED!")
print("="*80 + "\n")
