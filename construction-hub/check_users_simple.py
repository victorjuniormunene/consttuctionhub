#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

users = User.objects.all()
print(f'Total users: {users.count()}')
for u in users:
    print(f'{u.username}: {u.user_type}, active: {u.is_active}')
