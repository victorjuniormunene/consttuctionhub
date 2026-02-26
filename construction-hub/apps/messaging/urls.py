from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.my_conversations, name='conversations'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('conversation/<int:conversation_id>/send/', views.send_message, name='send_message'),
    path('order/<int:order_id>/start/', views.start_conversation, name='start_conversation'),
    path('api/conversations/', views.get_conversations_api, name='api_conversations'),
    path('api/conversations/<int:conversation_id>/messages/', views.get_messages_api, name='api_messages'),
    path('api/conversations/create/', views.create_conversation, name='api_create_conversation'),
]
