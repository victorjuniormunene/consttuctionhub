from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Supplier, Product

class SupplierModelTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.supplier = Supplier.objects.create(user=self.user, company_name="Test Supplier", location="Test Location")

    def test_supplier_creation(self):
        self.assertEqual(self.supplier.company_name, "Test Supplier")
        self.assertEqual(self.supplier.location, "Test Location")

class ProductModelTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.supplier = Supplier.objects.create(user=self.user, company_name="Test Supplier", location="Test Location")
        self.product = Product.objects.create(name="Test Product", cost=100.00, supplier=self.supplier)

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.cost, 100.00)
        self.assertEqual(self.product.supplier, self.supplier)
