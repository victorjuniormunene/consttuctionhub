from django.test import TestCase
from .models import Consultation

class ConsultationModelTest(TestCase):
    def setUp(self):
        self.consultation = Consultation.objects.create(
            customer_name="John Doe",
            email="john@example.com",
            phone="1234567890",
            message="Need consultation for building a house."
        )

    def test_consultation_creation(self):
        self.assertEqual(self.consultation.customer_name, "John Doe")
        self.assertEqual(self.consultation.email, "john@example.com")
        self.assertEqual(self.consultation.phone, "1234567890")
        self.assertEqual(self.consultation.message, "Need consultation for building a house.")

    def test_str_representation(self):
        self.assertEqual(str(self.consultation), "Consultation by John Doe")