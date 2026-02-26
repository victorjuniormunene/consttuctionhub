from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegistrationForm(forms.ModelForm):
    ROLE_CHOICES = (('customer', 'Customer'), ('supplier', 'Supplier'))
    username = forms.CharField(help_text="Required. 150 characters or fewer. Letters, digits and './+/-/_' only.", widget=forms.TextInput(attrs={'placeholder': 'obonyo'}))
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect, initial='customer')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'role')

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if not p1 or not p2 or p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        # store role on the user model if it has a user_type field
        if hasattr(user, 'user_type'):
            user.user_type = self.cleaned_data.get('role')
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)