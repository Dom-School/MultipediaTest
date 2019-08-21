from django import forms

class SearchForm(forms.Form):
    search = forms.CharField(label='Search',
                             max_length=100, 
                             widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'placeholder': 'Search',
                                                            'aria-label': 'Search' }))