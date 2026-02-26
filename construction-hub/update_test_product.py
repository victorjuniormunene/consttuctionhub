#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from apps.suppliers.models import Supplier
from apps.products.models import Product

print("\n" + "="*80)
print("UPDATING TEST PRODUCT TO RIVER SAND")
print("="*80)

try:
    # Get the test product by name
    product = Product.objects.get(name='Test Product for Supplier')

    # Update the product to River Sand
    product.name = 'River Sand'
    product.description = 'High quality river sand for construction purposes'
    product.category = 'other'
    product.location = 'River Location'
    product.cost = 99.99
    product.image_url = '/static/images/sand.jpg'

    product.save()

    print("  ✓ Product updated successfully")
    print(f"Name: {product.name}")
    print(f"Description: {product.description}")
    print(f"Category: {product.get_category_display()}")
    print(f"Location: {product.location}")
    print(f"Cost: KSH {product.cost}")
    print(f"Image URL: {product.image_url}")

except Product.DoesNotExist:
    print("  ❌ Product 'Test Product for Supplier' not found")
except Exception as e:
    print(f"  ❌ Error: {e}")

print("\n" + "="*80)
print("PRODUCT UPDATE COMPLETED!")
print("="*80 + "\n")
