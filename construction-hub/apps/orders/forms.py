from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    customer_name = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Customer full name (optional)',
    }))
    customer_number = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Customer phone number (optional)',
    }))
    customer_location = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Customer location/address (optional)',
    }))

    def __init__(self, *args, **kwargs):
        # Get product from kwargs
        product = kwargs.pop('product', None)
        super(OrderForm, self).__init__(*args, **kwargs)
        
        # Hide the offer field - offers are now automatically applied based on product
        # The offer will be set automatically when creating the order
        self.fields['offer'].widget.attrs['style'] = 'display:none;'
        self.fields['offer'].required = False
        
        # If product has an offer, pre-set it in the initial data
        if product and product.offer:
            self.initial['offer'] = product.offer
            # Also set the value directly on the field
            self.fields['offer'].initial = product.offer

    class Meta:
        model = Order
        fields = ['quantity', 'price', 'customer_name', 'customer_number', 'customer_location', 'offer']
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': '1',
                'max': '1000',
                'value': '1',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': '0.01',
                'step': '0.01',
                'placeholder': 'Price per unit (KSH)',
            }),
            'offer': forms.Select(attrs={
                'class': 'form-select',
            }),
        }
