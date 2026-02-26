from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_dashboard, name='dashboard'),
    path('customer/pdf/', views.customer_report_pdf, name='customer_pdf'),
    path('supplier/pdf/', views.supplier_report_pdf, name='supplier_pdf'),
    path('customer/excel/', views.customer_report_excel, name='customer_excel'),
    path('supplier/excel/', views.supplier_report_excel, name='supplier_excel'),
]
