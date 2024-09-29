from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class FilterForm(forms.Form):
    SORT_CHOICES = [
        ('-investmentmetrics__roi', 'ROI (High to Low)'),
        ('-city__population', 'Population (High to Low)'),
        ('-migrationdata__move_in_count', 'Move-Ins (High to Low)')
    ]
    sort_by = forms.ChoiceField(choices=SORT_CHOICES, required=False)



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
