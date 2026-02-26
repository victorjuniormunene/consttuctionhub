#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.orders.models import Order
from apps.suppliers.models import Supplier

def debug_orders():
    User = get_user_model()

    # Get all suppliers
    suppliers = Supplier.objects.all()
    print(f"Found {suppliers.count()} suppliers")

    for supplier in suppliers:
        print(f"\nSupplier: {supplier.user.username} ({supplier.company_name})")

        # Check orders created by this supplier
        created_orders = Order.objects.filter(ordering_supplier=supplier.user)
        print(f"  Orders created by supplier: {created_orders.count()}")

        for order in created_orders:
            print(f"    Order #{order.id} ({order.order_number}): {order.product.name} x {order.quantity}")

        # Check orders for this supplier's products
        product_orders = Order.objects.filter(product__supplier=supplier)
        print(f"  Orders for supplier's products: {product_orders.count()}")

        for order in product_orders:
            print(f"    Order #{order.id} ({order.order_number}): {order.product.name} x {order.quantity}")

if __name__ == '__main__':
    debug_orders()
