from django.contrib import admin
from .models import Product

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'supplier', 'category', 'cost', 'location')
    list_filter = ('category', 'supplier')
    search_fields = ('name', 'supplier__company_name')
    list_filter = ('supplier',)

admin.site.register(Product, ProductAdmin)