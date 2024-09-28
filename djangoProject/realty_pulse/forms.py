from django import forms

class FilterForm(forms.Form):
    SORT_CHOICES = [
        ('-investmentmetrics__roi', 'ROI (High to Low)'),
        ('-city__population', 'Population (High to Low)'),
        ('-migrationdata__move_in_count', 'Move-Ins (High to Low)')
    ]
    sort_by = forms.ChoiceField(choices=SORT_CHOICES, required=False)
