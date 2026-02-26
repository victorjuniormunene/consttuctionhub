#!/usr/bin/env python
"""
Test script to verify that the login page has all required frontend features:
- Two-column layout
- Welcome back message
- Google login option
- Facebook login option
- Reset password link
"""

def test_login_page_features():
    """Test that the login page contains all required features."""

    # Read the login template file
    try:
        with open('templates/accounts/login.html', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("✗ Login template file not found")
        return False

    tests = [
        ('Two-column layout', 'grid-template-columns: 1fr 1fr' in content or 'register-container' in content),
        ('Welcome back message', 'Welcome Back!' in content),
        ('Google login', 'Google' in content and 'provider_login_url \'google\'' in content),
        ('Facebook login', 'Facebook' in content and 'provider_login_url \'facebook\'' in content),
        ('Reset password link', 'Forgot your password?' in content and 'password_reset' in content),
    ]

    all_passed = True
    for feature, passed in tests:
        if passed:
            print(f"✓ {feature} - Present")
        else:
            print(f"✗ {feature} - Missing")
            all_passed = False

    return all_passed

if __name__ == '__main__':
    print("Testing login page frontend features...")
    success = test_login_page_features()
    if success:
        print("\n✓ All required features are present in the login page!")
    else:
        print("\n✗ Some features are missing from the login page.")
