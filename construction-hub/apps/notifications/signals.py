from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from apps.consultations.models import ConsultantApplication
from apps.orders.models import Order

@receiver(post_save, sender=ConsultantApplication)
def notify_admin_new_consultant_application(sender, instance, created, **kwargs):
    """Send email notification to admin when a new consultant application is submitted"""
    if created:
        subject = f'New Consultant Application: {instance.full_name}'
        message = f"""
        A new consultant application has been submitted.

        Applicant Details:
        - Name: {instance.full_name}
        - Email: {instance.email}
        - Phone: {instance.phone}
        - Specialization: {instance.specialization}
        - Experience: {instance.experience_years} years
        - Consultation Rate: KSH {instance.consultation_rate}

        Application submitted on: {instance.submitted_at.strftime('%Y-%m-%d %H:%M:%S')}

        Please review this application in the admin panel.
        """

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False,
            )
        except Exception as e:
            # Log the error but don't fail the application
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send consultant application notification: {e}")

@receiver(post_save, sender=Order)
def notify_admin_new_order(sender, instance, created, **kwargs):
    """Send email notification to admin when a new order is placed"""
    if created:
        subject = f'New Order Placed: {instance.order_number}'
        message = f"""
        A new order has been placed.

        Order Details:
        - Order Number: {instance.order_number}
        - Customer: {instance.customer_name or getattr(instance.customer, 'username', 'N/A')}
        - Product: {instance.product.name if instance.product else 'Plan: ' + str(instance.plan_type)}
        - Quantity: {instance.quantity}
        - Total Amount: KSH {instance.total_cost}
        - Status: {instance.get_status_display()}

        Order placed on: {instance.created_at.strftime('%Y-%m-%d %H:%M:%S')}

        Please review this order in the admin panel.
        """

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False,
            )
        except Exception as e:
            # Log the error but don't fail the order
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send new order notification: {e}")

@receiver(post_save, sender=Order)
def notify_customer_order_status_change(sender, instance, **kwargs):
    """Send email notification to customer when order status changes"""
    # Only send if this is an update (not creation) and status has changed
    if not kwargs.get('created', False) and hasattr(instance, '_original_status'):
        if instance.status != instance._original_status:
            subject = f'Order Status Update: {instance.order_number}'
            message = f"""
            Your order status has been updated.

            Order Details:
            - Order Number: {instance.order_number}
            - Product: {instance.product.name if instance.product else 'Plan: ' + str(instance.plan_type)}
            - Quantity: {instance.quantity}
            - Total Amount: KSH {instance.total_cost}
            - New Status: {instance.get_status_display()}

            Status updated on: {instance.updated_at.strftime('%Y-%m-%d %H:%M:%S')}

            If you have any questions, please contact our support team.
            """

            customer_email = getattr(instance.customer, 'email', None) or instance.customer_name
            if customer_email:
                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[customer_email],
                        fail_silently=False,
                    )
                except Exception as e:
                    # Log the error but don't fail the status update
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Failed to send order status notification: {e}")

def track_order_status_change(sender, instance, **kwargs):
    """Track the original status before saving for comparison"""
    if instance.pk:
        try:
            original = Order.objects.get(pk=instance.pk)
            instance._original_status = original.status
        except Order.DoesNotExist:
            pass

# Connect the tracking signal
from django.db.models.signals import pre_save
pre_save.connect(track_order_status_change, sender=Order)
