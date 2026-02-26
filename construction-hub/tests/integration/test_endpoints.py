from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.accounts.models import User
from apps.products.models import Product
from apps.orders.models import Order
from apps.consultations.models import Consultation

class EndpointTests(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='adminpass',
            email='admin@example.com'
        )
        self.supplier_user = User.objects.create_user(
            username='supplier',
            password='supplierpass',
            email='supplier@example.com',
            user_type='supplier'
        )
        self.customer_user = User.objects.create_user(
            username='customer',
            password='customerpass',
            email='customer@example.com',
            role='customer'
        )
        self.product = Product.objects.create(
            name='Concrete',
            price=100.00,
            supplier=self.supplier_user
        )
        self.consultation = Consultation.objects.create(
            customer=self.customer_user,
            details='Need advice on building plans'
        )

    def test_product_list(self):
        response = self.client.get(reverse('products:list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.product.name.encode(), response.content)

    def test_create_order(self):
        self.client.login(username='customer', password='customerpass')
        response = self.client.post(reverse('orders:create'), {
            'product': self.product.id,
            'quantity': 2
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

    def test_create_consultation(self):
        self.client.login(username='customer', password='customerpass')
        response = self.client.post(reverse('consultations:create'), {
            'details': 'Need help with my building project'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Consultation.objects.count(), 2)

    def test_admin_can_view_all_orders(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('orders:list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_supplier_can_post_product(self):
        self.client.login(username='supplier', password='supplierpass')
        response = self.client.post(reverse('products:create'), {
            'name': 'Steel',
            'price': 200.00,
            'supplier': self.supplier_user.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)