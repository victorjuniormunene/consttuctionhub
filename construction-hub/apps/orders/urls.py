from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('orders/', views.order_list, name='order_list'),
    path('orders/create/', views.order_create, name='order_create'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    # path('orders/<int:order_id>/delete/', views.order_delete, name='order_delete'),
    # path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('orders/<int:order_id>/payment/', views.payment, name='payment'),
    path('orders/<int:order_id>/receipt/download/', views.download_receipt, name='download_receipt'),
    path('orders/<int:order_id>/edit-supplier/', views.edit_supplier_order, name='edit_supplier_order'),
    path('orders/<int:order_id>/delete-supplier/', views.delete_supplier_order, name='delete_supplier_order'),
    path('orders/<int:order_id>/track/', views.order_tracking, name='order_tracking'),
    path('orders/<int:order_id>/mark-completed/', views.mark_order_completed, name='mark_order_completed'),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    path('manual-mpesa-update/', views.manual_mpesa_update, name='manual_mpesa_update'),
    path('api/orders/<int:order_id>/status/', views.get_order_status_api, name='order_status_api'),
]
