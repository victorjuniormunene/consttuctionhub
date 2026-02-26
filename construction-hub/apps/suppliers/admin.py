from django.contrib import admin
from .models import Supplier, Product


class SupplierAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'location', 'contact_number')
    search_fields = ('company_name', 'location')


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'supplier', 'category', 'cost', 'available_quantity')
    list_filter = ('category', 'supplier')
    list_filter = ('supplier', 'available_quantity')
    search_fields = ('name',)


admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Product, ProductAdmin)