#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from apps.products.models import Product

def update_product_stock():
    """Update all products to have 40 units in stock"""
    products = Product.objects.all()
    updated_count = 0

    for product in products:
        if product.available_quantity != 40:
            product.available_quantity = 40
            product.save()
            updated_count += 1
            print(f"Updated {product.name}: stock set to 40")

    print(f"\nTotal products updated: {updated_count}")
    print(f"Total products in database: {products.count()}")

if __name__ == '__main__':
    update_product_stock()
