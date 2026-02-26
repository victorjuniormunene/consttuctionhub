from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('<int:product_id>/edit/', views.product_update, name='product_update'),
    path('<int:product_id>/delete/', views.product_delete, name='product_delete'),
    path('create/', views.product_create, name='product_create'),
    path('<int:product_id>/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('cart/<int:cart_item_id>/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
]
