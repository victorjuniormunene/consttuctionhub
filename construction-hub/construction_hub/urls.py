"""
URL configuration for construction_hub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import path, include
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Custom accounts URLs must come BEFORE allauth.urls to ensure /accounts/login/ uses our custom view
    path('accounts/', include('apps.accounts.urls')),
    path('accounts/', include('allauth.urls')),
    path('social/', include('allauth.urls')),
    path('suppliers/', include('apps.suppliers.urls')),
    path('products/', include('apps.products.urls')),
    path('orders/', include('apps.orders.urls')),
    path('consultations/', include('apps.consultations.urls', namespace='consultations')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('reports/', include('apps.reports.urls')),
    path('messaging/', include('apps.messaging.urls', namespace='messaging')),
    path('', include('apps.accounts.urls')),  # Root URL for home page
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
