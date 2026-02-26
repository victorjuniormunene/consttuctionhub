from django.db import models
from apps.suppliers.models import Supplier

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

    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    image_url = models.URLField(blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    quality = models.CharField(max_length=50, choices=[
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('high_end', 'High-End'),
    ], default='standard', help_text="Quality level of the product")
    location = models.CharField(max_length=255)
    available_quantity = models.PositiveIntegerField(default=0)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='products_from_products_app')
    
    # Offer field for supplier offers
    offer = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('', 'No Offer'),
        ('free_delivery', 'Free Delivery'),
        ('10_percent_discount', '10% Discount'),
    ], help_text="Special offer applied to this product")

    def __str__(self):
        return self.name

class ProductOrder(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order of {self.quantity} x {self.product.name} by {self.customer_name}"