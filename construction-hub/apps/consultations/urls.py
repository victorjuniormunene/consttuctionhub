
from django.urls import path
from . import views

app_name = 'consultations'

urlpatterns = [
    path('select/', views.select_consultant, name='select_consultant'),
    path('<int:consultant_id>/confirm/', views.confirm_consultation_booking, name='confirm_consultation_booking'),
    path('<int:consultant_id>/pay/', views.consultation_payment, name='consultation_payment'),
    path('payment/callback/', views.consultation_mpesa_callback, name='consultation_mpesa_callback'),
    path('<int:consultation_id>/success/', views.consultation_success, name='consultation_success'),
    path('orders/<int:order_id>/receipt/customer/download/', views.download_order_receipt_customer, name='download_order_receipt_customer'),
    path('<int:consultation_id>/receipt/download/', views.download_consultation_receipt, name='download_consultation_receipt'),
    path('receipts/consultant/download/', views.download_consultation_receipt, name='download_consultation_receipts_consultant'),
    path('<int:consultation_id>/mark-completed/', views.mark_consultation_completed, name='mark_consultation_completed'),
    path('qualification-form/download/', views.download_qualification_form, name='download_qualification_form'),
    path('profile/download/', views.download_profile_pdf, name='download_profile_pdf'),
]
