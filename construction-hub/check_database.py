#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.suppliers.models import Supplier, Product
from apps.orders.models import Order

User = get_user_model()

print("\n" + "="*80)
print("DATABASE INVENTORY CHECK")
print("="*80)

print("\n🔹 USERS:")
users = User.objects.all()
for u in users[:15]:
    is_supplier = getattr(u, 'is_supplier', False)
    print(f"  {u.id:2}: {u.username:20} | is_supplier: {is_supplier}")

print(f"\nTotal Users: {users.count()}")

print("\n🔹 SUPPLIERS:")
suppliers = Supplier.objects.all()
for s in suppliers:
    print(f"  {s.id}: {s.company_name:30} | User: {s.user.username}")

print(f"Total Suppliers: {suppliers.count()}")

print("\n🔹 PRODUCTS:")
products = Product.objects.all()
for p in products[:15]:
    print(f"  {p.id:2}: {p.name:25} | Cost: {p.cost:8} KSH | Stock: {p.available_quantity:3} | Supplier: {p.supplier.company_name}")

print(f"Total Products: {products.count()}")

print("\n🔹 ORDERS:")
orders = Order.objects.all()
if orders.count() == 0:
    print("  No orders yet.")
else:
    for o in orders[:20]:
        customer_info = o.customer.username if o.customer else f"(None - name: {o.customer_name})"
        print(f"  {o.id:2}: {o.order_number:12} | {o.quantity:2}x {o.product.name:25} | Customer: {customer_info:20} | Status: {o.status}")

print(f"Total Orders: {orders.count()}")
print("\n" + "="*80)
print("✅ Database is ready! You can:")
print("   1. Create orders via the UI at http://127.0.0.1:8000/orders/create/")
print("   2. Supplier creates orders at http://127.0.0.1:8000/suppliers/create-order/")
print("   3. View orders in dashboards")
print("="*80 + "\n")
