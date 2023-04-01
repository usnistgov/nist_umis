""" forms for the API home page """
from django import forms


class SearchForm(forms.Form):
    """ enter a search term on /api/home """
    term = forms.CharField(label='Search for a unit', max_length=32)