""" view file for the quantitites app """
from django.shortcuts import render
from units.models import *


def index(request):
    """ show a list of quantities """
    quants = Quantities.objects.all().order_by('name')
    return render(request, "../templates/quantities/index.html", {'quants': quants})


def view(request, qid):
    """ show data about a single quantity """
    quant = Quantities.objects.get(id=qid)
    qkindid = Quantities.objects.get(id=qid).quantitykind_id
    unitids = QuantitykindsUnits.objects.filter(quantitykind_id=qkindid).values_list('unit_id', flat=True)
    units = Units.objects.filter(id__in=unitids)
    return render(request, "../templates/quantities/view.html", {'quant': quant, 'units': units})
