from django.shortcuts import render
from units.models import *


def index(request):
    quants = Quantities.objects.all().order_by('name')
    return render(request, "../templates/quantities/index.html", {'quants': quants})


def view(request, qid):
    quant = Quantities.objects.get(id=qid)
    qkindid = Quantities.objects.get(id=qid).quantitykind_id
    unitids = QuantitykindsUnits.objects.filter(quantitykind_id=qkindid)
    units = Units.objects.filter(id__in=unitids)
    return render(request, "../templates/quantities/view.html", {'quant': quant, 'units': units})
