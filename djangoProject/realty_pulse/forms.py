from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from realty_pulse.models import City


class FilterForm(forms.Form):
    SORT_CHOICES = [
        ('-roi', 'ROI (High to Low)'),
        ('roi', 'ROI (Low to High)'),
        ('-income', 'Income (High to Low)'),
        ('income', 'Income (Low to High)'),
    ]
    sort_by = forms.ChoiceField(choices=SORT_CHOICES, required=False, label="Sort By")

    income = forms.IntegerField(required=False, min_value=0, max_value=150000, label="Filter by Income")

    city = forms.CharField(required=False, label="Select City")
    year = forms.IntegerField(required=False, min_value=2024, max_value=2030, label="Select Year")


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

        # Adding custom widgets or labels if needed
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    # Override the clean method to add custom validation
    def clean_username(self):
        username = self.cleaned_data.get('username')

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken. Please choose another.')

        return username
