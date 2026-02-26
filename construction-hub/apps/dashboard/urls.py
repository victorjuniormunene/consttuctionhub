from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.customer_dashboard_view, name='customer_dashboard'),
    path('consultant/', views.consultant_dashboard_view, name='consultant_dashboard'),
    path('supplier/', views.supplier_dashboard_view, name='supplier_dashboard'),
    path('order-history/', views.order_history_view, name='order_history'),
    path('consultation-requests/', views.consultation_requests_view, name='consultation_requests'),
    path('download-customer-report/', views.download_customer_report, name='download_customer_report'),
    path('download-supplier-report/', views.download_supplier_report, name='download_supplier_report'),
    path('download-consultant-report/', views.download_consultant_report, name='download_consultant_report'),
    path('send-consultant-email/', views.send_consultant_email, name='send_consultant_email'),
]
