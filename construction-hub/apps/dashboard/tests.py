from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from apps.orders.models import Order
from apps.products.models import Product
from apps.suppliers.models import Supplier

class DashboardTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        self.supplier = Supplier.objects.create(
            user=self.user,
            company_name='Test Supplier'
        )
        self.product = Product.objects.create(
            name='Test Product',
            cost=100.00,
            supplier=self.supplier
        )

    def test_customer_dashboard_shows_supplier_created_orders(self):
        """Test that supplier-created orders appear in customer dashboard with partial name matching"""
        # Create an order with customer_name that partially matches user's full name
        order = Order.objects.create(
            product=self.product,
            customer=None,  # Supplier-created order
            customer_name='Test User',  # Exact match with full name
            quantity=1
        )

        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('accounts:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(order, response.context['orders'])

    def test_customer_dashboard_shows_orders_with_partial_name_match(self):
        """Test that orders appear with partial name matching"""
        # Create an order with customer_name that is a substring of user's full name
        order = Order.objects.create(
            product=self.product,
            customer=None,
            customer_name='Test',  # Partial match
            quantity=1
        )

        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('accounts:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(order, response.context['orders'])

    def test_customer_dashboard_shows_orders_with_username_match(self):
        """Test that orders appear when customer_name matches username"""
        order = Order.objects.create(
            product=self.product,
            customer=None,
            customer_name='testuser',  # Matches username
            quantity=1
        )

        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('accounts:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(order, response.context['orders'])
