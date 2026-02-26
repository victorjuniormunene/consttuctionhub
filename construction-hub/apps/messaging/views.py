from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q
import json
from .models import Conversation, Message
from apps.orders.models import Order
from apps.suppliers.models import Supplier


@login_required
def my_conversations(request):
    user = request.user
    # Only allow suppliers to access the messages page directly
    # Customers should use the dashboard to message suppliers
    if not user.is_supplier:
        messages.error(request, "You do not have access to the messages page.")
        return redirect("accounts:dashboard")
    conversations = Conversation.objects.filter(
        Q(customer=user) | Q(supplier=user)
    ).select_related("order", "customer", "supplier").prefetch_related("messages")
    context = {"conversations": conversations}
    return render(request, "messaging/conversations.html", context)


@login_required
def conversation_detail(request, conversation_id):
    try:
        conversation = Conversation.objects.get(
            Q(id=conversation_id, customer=request.user) | 
            Q(id=conversation_id, supplier=request.user)
        )
    except Conversation.DoesNotExist:
        raise Http404("Conversation not found")
    
    Message.objects.filter(conversation=conversation, is_read=False).exclude(sender=request.user).update(is_read=True)
    context = {"conversation": conversation, "messages": conversation.messages.all()}
    return render(request, "messaging/conversation_detail.html", context)


@login_required
@require_http_methods(["POST"])
def send_message(request, conversation_id):
    try:
        conversation = Conversation.objects.get(
            Q(id=conversation_id, customer=request.user) | 
            Q(id=conversation_id, supplier=request.user)
        )
    except Conversation.DoesNotExist:
        return JsonResponse({"success": False, "error": "Conversation not found"}, status=404)
    
    try:
        data = json.loads(request.body)
        content = data.get("content", "").strip()
        if not content:
            return JsonResponse({"success": False, "error": "Message cannot be empty"}, status=400)
        message = Message.objects.create(conversation=conversation, sender=request.user, content=content)
        conversation.updated_at = timezone.now()
        conversation.save()
        return JsonResponse({"success": True, "message": {"id": message.id, "content": message.content, "sender": message.sender.username, "created_at": message.created_at.strftime("%b %d, %Y %H:%M"), "is_me": True}})
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid request"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
def start_conversation(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    if not order.product or not hasattr(order.product, "supplier"):
        messages.error(request, "This order does not have a supplier.")
        return redirect("dashboard:customer_dashboard")
    supplier_user = order.product.supplier.user
    conversation, created = Conversation.objects.get_or_create(order=order, customer=request.user, supplier=supplier_user)
    return redirect("messaging:conversation_detail", conversation_id=conversation.id)


@login_required
@require_http_methods(["POST"])
def create_conversation(request):
    try:
        data = json.loads(request.body)
        order_id = data.get("order_id")
        initial_message = data.get("message", "").strip()
        order = get_object_or_404(Order, id=order_id, customer=request.user)
        if not order.product or not hasattr(order.product, "supplier"):
            return JsonResponse({"success": False, "error": "No supplier associated with this order"}, status=400)
        supplier_user = order.product.supplier.user
        conversation, created = Conversation.objects.get_or_create(order=order, customer=request.user, supplier=supplier_user)
        if initial_message:
            Message.objects.create(conversation=conversation, sender=request.user, content=initial_message)
        return JsonResponse({"success": True, "conversation_id": conversation.id, "created": created})
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid request"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
def get_conversations_api(request):
    user = request.user
    conversations = Conversation.objects.filter(Q(customer=user) | Q(supplier=user)).select_related("order", "customer", "supplier").prefetch_related("messages")
    data = []
    for conv in conversations:
        last_msg = conv.last_message
        data.append({"id": conv.id, "order_number": conv.order.order_number, "product_name": conv.order.product.name if conv.order.product else "N/A", "other_user": conv.supplier.username if conv.customer == user else conv.customer.username, "last_message": last_msg.content[:50] + "..." if last_msg else "No messages yet", "last_message_time": last_msg.created_at.strftime("%b %d, %H:%M") if last_msg else "", "unread_count": conv.unread_count, "created_at": conv.created_at.strftime("%b %d, %Y")})
    return JsonResponse({"conversations": data})


@login_required
def get_messages_api(request, conversation_id):
    try:
        conversation = Conversation.objects.get(
            Q(id=conversation_id, customer=request.user) | 
            Q(id=conversation_id, supplier=request.user)
        )
    except Conversation.DoesNotExist:
        return JsonResponse({"error": "Conversation not found"}, status=404)
    
    Message.objects.filter(conversation=conversation, is_read=False).exclude(sender=request.user).update(is_read=True)
    messages = conversation.messages.all()
    data = []
    for msg in messages:
        data.append({"id": msg.id, "content": msg.content, "sender": msg.sender.username, "is_me": msg.sender == request.user, "created_at": msg.created_at.strftime("%b %d, %Y %H:%M"), "is_read": msg.is_read})
    return JsonResponse({"messages": data})
