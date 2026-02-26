from django.db import models
from django.conf import settings


class Supplier(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    contact_number = models.CharField(max_length=15, blank=True)
    # Consultation fee (optional) — used when suppliers act as consultants
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return self.company_name or getattr(self.user, 'username', 'supplier')


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('cement', 'Cement & Concrete'),
        ('steel', 'Steel & Metals'),
        ('wood', 'Wood & Timber'),
        ('electrical', 'Electrical'),
        ('plumbing', 'Plumbing'),
        ('tools', 'Tools & Equipment'),
        ('other', 'Other'),
    ]

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='supplier_products')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)
    available_quantity = models.PositiveIntegerField(default=0)
    
    # Offer field for supplier offers
    offer = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('', 'No Offer'),
        ('free_delivery', 'Free Delivery'),
        ('10_percent_discount', '10% Discount'),
    ], help_text="Special offer applied to this product")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
