from django import forms
from .models import Product
from apps.orders.models import Order


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('name', 'description', 'category', 'cost', 'available_quantity', 'offer')


class SupplierOrderForm(forms.Form):
    # Product name selection from predefined list
    PRODUCT_CHOICES = [
        ('', 'Select Product'),
        ('cement', 'Cement'),
        ('sand', 'Sand'),
        ('wire', 'Wire'),
        ('steel', 'Steel'),
        ('timber', 'Timber'),
        ('steel rebar', 'Steel Rebar'),
        ('bricks', 'Bricks'),
    ]

    # Offer choices
    OFFER_CHOICES = [
        ('', 'No Offer'),
        ('free_delivery', 'Free Delivery'),
        ('10_percent_discount', '10% Discount'),
    ]
    
    offer = forms.ChoiceField(
        choices=OFFER_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    product_name = forms.ChoiceField(
        choices=PRODUCT_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    # Product image upload
    product_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    # Order details
    quantity = forms.IntegerField(
        min_value=1,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter quantity'
        })
    )

    # Product price
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter price per unit',
            'step': '0.01'
        })
    )

    # Stock quantity
    available_quantity = forms.IntegerField(
        min_value=0,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter stock quantity'
        })
    )

    # Supplier information (editable)
    supplier_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter supplier name'
        })
    )
    supplier_phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter supplier phone number'
        })
    )
    supplier_location = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter supplier location'
        })
    )



    def __init__(self, *args, **kwargs):
        supplier = kwargs.pop('supplier', None)
        super().__init__(*args, **kwargs)

        if supplier:
            # Pre-fill supplier information
            self.fields['supplier_name'].initial = supplier.company_name or supplier.user.username
            self.fields['supplier_phone'].initial = supplier.contact_number or 'N/A'
            self.fields['supplier_location'].initial = supplier.location or 'N/A'

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')

        if product and quantity:
            if quantity > product.available_quantity:
                raise forms.ValidationError(
                    f"Only {product.available_quantity} units available in stock."
                )

        return cleaned_data
