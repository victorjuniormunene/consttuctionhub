from django.test import TestCase
from .models import Order
from django.contrib.auth import get_user_model

User = get_user_model()

class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.order = Order.objects.create(
            user=self.user,
            product_name='Concrete',
            quantity=10,
            total_cost=500.00
        )

    def test_order_creation(self):
        self.assertEqual(self.order.user.username, 'testuser')
        self.assertEqual(self.order.product_name, 'Concrete')
        self.assertEqual(self.order.quantity, 10)
        self.assertEqual(self.order.total_cost, 500.00)

    def test_order_str(self):
        self.assertEqual(str(self.order), f'Order {self.order.id} by {self.order.user.username}')

    def test_order_total_cost_calculation(self):
        self.order.quantity = 5
        self.order.total_cost = self.order.quantity * 50.00  # Assuming cost per unit is 50
        self.order.save()
        self.assertEqual(self.order.total_cost, 250.00)

class OrderViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_order_list_view(self):
        response = self.client.get('/orders/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_list.html')

    def test_order_create_view(self):
        response = self.client.post('/orders/create/', {
            'product_name': 'Steel',
            'quantity': 20,
            'total_cost': 1000.00
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertTrue(Order.objects.filter(product_name='Steel').exists())