from django.urls import path
from . import views

app_name = 'suppliers'

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/add/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_update, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('create-order/', views.create_order_for_supplier, name='create_order'),
    path('sell-all-orders/', views.sell_all_orders, name='sell_all_orders'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
]
