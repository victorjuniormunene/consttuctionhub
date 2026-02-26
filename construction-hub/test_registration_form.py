#!/usr/bin/env python
"""
Test script to verify that the registration form only shows customer and supplier roles.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_hub.settings')
django.setup()

from apps.accounts.forms import UserRegistrationForm

def test_registration_form_roles():
    """Test that UserRegistrationForm only has customer and supplier roles."""
    form = UserRegistrationForm()

    # Get the choices from the role field
    role_field = form.fields['role']
    choices = role_field.choices

    print("Registration Form Role Choices:")
    for choice_value, choice_label in choices:
        print(f"  - {choice_value}: {choice_label}")

    # Expected choices
    expected_choices = [('customer', 'Customer'), ('supplier', 'Supplier')]
    actual_choices = list(choices)

    if actual_choices == expected_choices:
        print("\n✓ SUCCESS: Registration form only shows customer and supplier roles")
        return True
    else:
        print(f"\n✗ FAILURE: Expected {expected_choices}, got {actual_choices}")
        return False

if __name__ == '__main__':
    success = test_registration_form_roles()
    sys.exit(0 if success else 1)
