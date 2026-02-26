from django.db import models
from django.conf import settings
from decimal import Decimal
from apps.products.models import Product
from django.core.files.storage import default_storage


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.quantity})"

    @property
    def total_cost(self):
        return self.product.cost * self.quantity


class Order(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    ordering_supplier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='supplier_orders', null=True, blank=True, help_text="Supplier who created this order")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Price per unit in KSH at time of order")
    order_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    customer_name = models.CharField(max_length=255, blank=True)
    customer_number = models.CharField(max_length=15, blank=True)
    customer_location = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=30, choices=[
        ('saved', 'Saved'),
        ('pending_payment', 'Pending Payment'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('complete_waiting_transport', 'Complete Waiting for Transport'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ], default='saved')
    order_image = models.ImageField(upload_to='order_images/', blank=True, null=True, help_text="Image uploaded by supplier when creating order")
    plan_type = models.CharField(max_length=50, blank=True, null=True, help_text="Type of architectural plan purchased (2_bedroom, 3_bedroom)")

    # M-Pesa Payment Fields
    mpesa_phone_number = models.CharField(max_length=15, blank=True, null=True, help_text="Customer's M-Pesa phone number")
    mpesa_transaction_id = models.CharField(max_length=50, blank=True, null=True, help_text="M-Pesa transaction ID")
    mpesa_checkout_request_id = models.CharField(max_length=50, blank=True, null=True, help_text="M-Pesa checkout request ID")
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ], default='pending', help_text="M-Pesa payment status")
    payment_initiated_at = models.DateTimeField(blank=True, null=True, help_text="When payment was initiated")
    payment_completed_at = models.DateTimeField(blank=True, null=True, help_text="When payment was completed")
    
    # Offer field for supplier offers
    offer = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('', 'No Offer'),
        ('free_delivery', 'Free Delivery'),
        ('10_percent_discount', '10% Discount'),
    ], help_text="Special offer applied to this order")

    @property
    def total_cost(self):
        """Calculate total cost using stored price or product cost"""
        unit_price = self.price if self.price else (self.product.cost if self.product else 0)
        total = unit_price * self.quantity
        
        # Apply 10% discount if offer is '10_percent_discount'
        if self.offer and '10_percent' in str(self.offer):
            discount_amount = total * Decimal('0.10')
            total = total - discount_amount
        
        return total
    
    def notify_supplier_low_stock(self):
        """Send notification to supplier when product quantity reaches 1"""
        from django.core.mail import send_mail
        from django.conf import settings

        subject = f"Low Stock Alert: {self.product.name}"
        message = f"""
        Dear {self.product.supplier.company_name},

        This is an automated notification to inform you that the stock level for your product "{self.product.name}" has reached 1 unit.

        Current stock: {self.product.available_quantity} units

        Please restock this product as soon as possible to ensure continued availability for customer orders.

        Product Details:
        - Name: {self.product.name}
        - Category: {self.product.get_category_display()}
        - Current Price: KSH {self.product.cost}

        Thank you for your attention to this matter.

        Best regards,
        Construction Hub Team
        """

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.product.supplier.user.email],
                fail_silently=False,
            )
        except Exception as e:
            # Log the error but don't fail the order
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send low stock notification: {e}")

    def notify_supplier_order_warning(self):
        """Send warning to supplier when order would leave low stock"""
        from django.core.mail import send_mail
        from django.conf import settings

        potential_quantity = self.product.available_quantity - self.quantity

        subject = f"Order Warning: Low Stock After Order - {self.product.name}"
        message = f"""
        Dear {self.product.supplier.company_name},

        This is an automated warning about a pending order for your product "{self.product.name}".

        Order Details:
        - Order ID: {self.order_number or self.id}
        - Quantity Ordered: {self.quantity} units
        - Current Stock: {self.product.available_quantity} units
        - Stock After Order: {potential_quantity} units

        This order would leave your product with very low stock ({potential_quantity} units remaining).
        Please consider restocking this product soon to ensure continued availability.

        Product Details:
        - Name: {self.product.name}
        - Category: {self.product.get_category_display()}
        - Current Price: KSH {self.product.cost}

        Thank you for your attention to this matter.

        Best regards,
        Construction Hub Team
        """

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.product.supplier.user.email],
                fail_silently=False,
            )
        except Exception as e:
            # Log the error but don't fail the order
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send order warning notification: {e}")

    def __str__(self):
        product_name = self.product.name if self.product else f"Plan: {self.plan_type}"
        return f"Order {self.id} by {getattr(self.customer, 'username', str(self.customer))} for {self.quantity} of {product_name}"

    def save(self, *args, **kwargs):
        """Capture product price at time of order if not already set"""
        # Capture the price at order creation time (only if product exists)
        if not self.price and self.product:
            self.price = self.product.cost

        # Call parent save first to ensure PK is set
        super().save(*args, **kwargs)
        # After PK is set, generate order_number if not already set
        if not self.order_number:
            self.order_number = f"ORD-{self.pk:08d}"
            # Update only the order_number field to avoid recursion
            super().save(update_fields=['order_number'])

        # Reduce product quantity after order is saved (only if product exists)
        if self.status in ['paid', 'completed'] and self.product:
            self.product.available_quantity -= self.quantity
            self.product.save()

            # Notify supplier if quantity reaches 1
            if self.product.available_quantity == 1:
                self.notify_supplier_low_stock()
        elif self.status == 'saved' and self.product:
            # For saved orders, check if quantity would leave only 1 or less
            potential_quantity = self.product.available_quantity - self.quantity
            if potential_quantity <= 1:
                # Send warning but don't reduce stock yet
                self.notify_supplier_order_warning()
