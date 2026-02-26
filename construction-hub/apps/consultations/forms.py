from django import forms
from apps.suppliers.models import Supplier
from .models import Consultation


class ConsultationForm(forms.ModelForm):
    supplier = forms.ModelChoiceField(queryset=Supplier.objects.all(), label='Consultant (supplier)')
    date_scheduled = forms.DateTimeField(label='Preferred date/time', required=False, widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD HH:MM'}))

    class Meta:
        model = Consultation
        fields = ('supplier', 'date_scheduled', 'details')
