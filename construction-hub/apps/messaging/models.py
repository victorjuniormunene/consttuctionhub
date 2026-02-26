from django.db import models
from django.contrib.auth import get_user_model
from apps.orders.models import Order

User = get_user_model()


class Conversation(models.Model):
    """
    Represents a conversation thread between a customer and supplier about an order.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='conversations')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_conversations')
    supplier = models.ForeignKey(User, on_delete=models.CASCADE, related_name='supplier_conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        unique_together = ['order', 'customer', 'supplier']
    
    def __str__(self):
        return f"Conversation #{self.id} - Order {self.order.order_number}"
    
    @property
    def last_message(self):
        return self.messages.first()
    
    @property
    def unread_count(self):
        return self.messages.filter(is_read=False).exclude(sender=self.customer).count()


class Message(models.Model):
    """
    Represents a message in a conversation between customer and supplier.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message by {self.sender.username} at {self.created_at}"
