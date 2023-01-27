""" calculation forms """
from django import forms
from calculations.models import *


class CalculateForm(forms.Form):
    """ form to guide the user to do a calculation """
    fquantids = Equations.objects.all().values_list('fquant', flat=True).distinct()
    fquants = Quantities.objects.filter(id__in=fquantids).values('id', 'name')
    fq = forms.IntegerField(label="Starting quantity", widget=forms.Select(choices=fquants))
