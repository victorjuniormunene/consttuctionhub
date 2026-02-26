from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class CustomUser(AbstractUser):
    USER_TYPES = [
        ('customer', 'Customer'),
        ('supplier', 'Supplier'),
        ('consultant', 'Consultant'),
        ('admin', 'Admin'),
    ]

    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='customer')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    @property
    def is_supplier(self):
        return self.user_type == 'supplier'

    @property
    def is_consultant(self):
        return self.user_type == 'consultant'

    def __str__(self):
        return self.username


class Customer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='customer_profile')
    # Additional customer-specific fields can be added here

    def __str__(self):
        return f"Customer: {self.user.username}"


class ArchitecturalPlan(models.Model):
    PLAN_TYPES = [
        ('2_bedroom', '2 Bedroom Plan'),
        ('3_bedroom', '3 Bedroom Plan'),
    ]
    
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    features = models.JSONField(default=list)
    plan_file = models.FileField(upload_to='architectural_plans/', help_text="PDF file of the architectural plan")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    # Reply fields
    admin_reply = models.TextField(blank=True, default='')
    replied_at = models.DateTimeField(null=True, blank=True)
    is_replied = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name}: {self.subject or 'No subject'}"

    class Meta:
        ordering = ['-submitted_at']


class PlanPurchase(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='plan_purchases')
    plan = models.ForeignKey(ArchitecturalPlan, on_delete=models.CASCADE)
    purchase_number = models.CharField(max_length=50, unique=True, blank=True)
    customer_name = models.CharField(max_length=255, default='John Victor')
    customer_phone = models.CharField(max_length=15, default='0708841408')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # M-Pesa Payment Fields
    mpesa_phone_number = models.CharField(max_length=15, blank=True, null=True)
    mpesa_transaction_id = models.CharField(max_length=50, blank=True, null=True)
    mpesa_checkout_request_id = models.CharField(max_length=50, blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    payment_initiated_at = models.DateTimeField(blank=True, null=True)
    payment_completed_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Purchase {self.purchase_number} - {self.plan.name}"

    def save(self, *args, **kwargs):
        if not self.purchase_number:
            super().save(*args, **kwargs)  # Save first to get ID
            self.purchase_number = f"PLAN-{self.pk:08d}"
            self.save(update_fields=['purchase_number'])
        else:
            super().save(*args, **kwargs)
