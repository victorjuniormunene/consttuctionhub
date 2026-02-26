from django.test import TestCase, Client
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from .models import Product

class ProductModelTest(TestCase):

    def setUp(self):
        self.product = Product.objects.create(
            name="Test Product",
            description="A product for testing purposes.",
            cost=100.00,
            location="Warehouse A"
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.description, "A product for testing purposes.")
        self.assertEqual(self.product.cost, 100.00)
        self.assertEqual(self.product.location, "Warehouse A")

    def test_product_str(self):
        self.assertEqual(str(self.product), "Test Product")

class ProductImageTest(StaticLiveServerTestCase):

    def setUp(self):
        self.client = Client()

    def test_concrete_mix_image_exists(self):
        response = self.client.get('/static/images/concrete mix.jpg')
        self.assertEqual(response.status_code, 200)

    def test_electrical_wires_image_exists(self):
        response = self.client.get('/static/images/electrical wires.jpg')
        self.assertEqual(response.status_code, 200)

    def test_steel_reinforcement_image_exists(self):
        response = self.client.get('/static/images/steel reinforcement.jpg')
        self.assertEqual(response.status_code, 200)

    def test_steel_rebars_image_exists(self):
        response = self.client.get('/static/images/Steel-Rebars.jpg')
        self.assertEqual(response.status_code, 200)
