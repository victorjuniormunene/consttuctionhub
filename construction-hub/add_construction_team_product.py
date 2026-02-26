#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from apps.suppliers.models import Supplier
from apps.products.models import Product

print("\n" + "="*80)
print("ADDING CONSTRUCTION TEAM PRODUCT")
print("="*80)

try:
    # Get the first supplier (or any supplier)
    supplier = Supplier.objects.first()
    if not supplier:
        print("  ❌ No suppliers found in database")
        exit(1)

    # Create the Construction Team product
    product, created = Product.objects.get_or_create(
        supplier=supplier,
        name='Construction Team',
        defaults={
            'description': 'Experienced builders and craftsmen dedicated to quality workmanship.',
            'category': 'other',
            'location': 'Nairobi',
            'cost': 5000.00,
            'image_url': '/static/images/construction team.jpg',
        }
    )

    if created:
        print("  ✓ Construction Team product created successfully")
    else:
        print("  ~ Construction Team product already exists")

    print(f"Product: {product.name}")
    print(f"Supplier: {product.supplier.company_name}")
    print(f"Description: {product.description}")
    print(f"Cost: KSH {product.cost}")
    print(f"Image: {product.image_url}")

except Exception as e:
    print(f"  ❌ Error: {e}")

print("\n" + "="*80)
print("CONSTRUCTION TEAM PRODUCT ADDITION COMPLETED!")
print("="*80 + "\n")
