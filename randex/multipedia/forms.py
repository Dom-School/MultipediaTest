from django import forms


class SearchForm(forms.Form):
    search_attrs = {'class': 'form-control',
                    'placeholder': 'Search',
                    'aria-label': 'Search',
                    "autocomplete": "off"}

    search = forms.CharField(label='Search',
                             max_length=100,
                             widget=forms.TextInput(attrs=search_attrs))
