#!/usr/bin/env python
"""
Debug script for PDF download issues
"""
import os
import django
import sys

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.orders.models import Order
from apps.consultations.models import Consultation
from apps.suppliers.models import Supplier

User = get_user_model()

print('=== DEBUGGING PDF DOWNLOAD ISSUES ===\n')

# Check users and their roles
users = User.objects.all()
print(f'Total users: {users.count()}')
for user in users:
    print(f'  - {user.username}: role={getattr(user, "role", "None")}, is_customer={getattr(user, "is_customer", False)}, is_supplier={getattr(user, "is_supplier", False)}, is_consultant={getattr(user, "is_consultant", False)}')

print()

# Check data counts
print('Data counts:')
print(f'  - Orders: {Order.objects.count()}')
print(f'  - Consultations: {Consultation.objects.count()}')
print(f'  - Suppliers: {Supplier.objects.count()}')

print()

# Check if users have data
for user in users:
    orders = Order.objects.filter(customer=user)
    consultations = Consultation.objects.filter(customer=user)
    print(f'{user.username} data:')
    print(f'  - Orders: {orders.count()}')
    print(f'  - Consultations: {consultations.count()}')

    # Check consultant data
    consultant_consultations = Consultation.objects.filter(consultant=user)
    print(f'  - Consultant consultations: {consultant_consultations.count()}')

    # Check supplier data
    try:
        supplier = Supplier.objects.get(user=user)
        supplier_orders = Order.objects.filter(product__supplier=supplier)
        print(f'  - Supplier orders: {supplier_orders.count()}')
    except Supplier.DoesNotExist:
        print(f'  - Supplier profile: None')
    print()

print('=== CHECKING CONSULTATION MODEL ===')
consultations = Consultation.objects.all()
for cons in consultations:
    print(f'Consultation {cons.id}: customer={cons.customer.username if cons.customer else None}, consultant={cons.consultant.username if cons.consultant else None}, consultant_name={cons.consultant_name}')
