from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from ..orders import views as order_views

app_name = 'accounts'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.unified_login, name='login'),
    path('customer-login/', views.customer_login, name='customer_login'),
    path('supplier-login/', views.supplier_login, name='supplier_login'),
    path('consultant-login/', views.consultant_login, name='consultant_login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # Provide a convenient /accounts/profile/ URL so default login redirect doesn't 404
    path('profile/', views.dashboard, name='profile'),
    path('consultant-application/', views.consultant_application, name='consultant_application'),
    path('consultant-applications/', views.my_consultant_applications, name='my_consultant_applications'),
    path('contact/', views.contact, name='contact'),
    path('pricing/', views.pricing, name='pricing'),
    path('about/', views.about, name='about'),
    path('purchase_plan/<str:plan_type>/', views.purchase_plan, name='purchase_plan'),
    path('complete_payment/<int:order_id>/', views.complete_payment, name='complete_payment'),
    path('download_plan/<str:plan_type>/', views.download_plan, name='download_plan'),
    path('download_plan_receipt/<str:plan_type>/', views.download_plan_receipt, name='download_plan_receipt'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html', email_template_name='accounts/password_reset_email.html', success_url='/accounts/password_reset/done/'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html', success_url='/accounts/reset/done/'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
]
