from django.db import models
from django.conf import settings


class Consultation(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='consultations')
    supplier = models.ForeignKey('suppliers.Supplier', on_delete=models.CASCADE, related_name='consultation_requests', null=True, blank=True)
    consultant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_consultations')
    
    # Store consultant info at booking time
    consultant_name = models.CharField(max_length=255, blank=True)
    consultant_phone = models.CharField(max_length=50, blank=True)
    consultation_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    specialization = models.CharField(max_length=255, blank=True)
    
    date_requested = models.DateTimeField(auto_now_add=True)
    date_scheduled = models.DateTimeField(null=True, blank=True)
    details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('pending_payment', 'Pending Payment'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ], default='pending')
    consultant_receipt_downloaded_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp when consultant downloaded the receipt")
    
    # M-Pesa Payment Fields
    mpesa_checkout_request_id = models.CharField(max_length=50, blank=True, null=True, help_text="M-Pesa checkout request ID")
    mpesa_transaction_id = models.CharField(max_length=50, blank=True, null=True, help_text="M-Pesa transaction ID")
    mpesa_phone_number = models.CharField(max_length=15, blank=True, null=True, help_text="Customer's M-Pesa phone number")

    def __str__(self):
        return f"Consultation {self.id} - {getattr(self.customer, 'username', str(self.customer))} with {self.consultant_name}"


class ConsultantApplication(models.Model):
    """Stores applications from users who want to become consultants/suppliers."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='consultant_applications', null=True, blank=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    specialization = models.CharField(max_length=255, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    consultation_rate = models.DecimalField(max_digits=10, decimal_places=2, default=5000, help_text="Consultation rate in KSH per hour/session")
    cover_letter = models.TextField(blank=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    cv = models.FileField(upload_to='cvs/', null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_consultant_applications'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    # Rejection fields
    rejected = models.BooleanField(default=False)
    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rejected_consultant_applications'
    )
    rejected_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, help_text="Reason for rejecting the application")

    def __str__(self):
        return f"ConsultantApplication {self.id} - {self.full_name}"
