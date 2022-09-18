from django.shortcuts import render
from units.models import *


def index(request):
    quants = Quantities.objects.all().order_by('name')
    return render(request, "../templates/quantities/index.html", {'quants': quants})


def view(request, qid):
    quant = Quantities.objects.get(id=qid)
    units = Units.objects.filter(quantitykind__quantities__id=qid)
    return render(request, "../templates/quantities/view.html", {'quant': quant, 'units': units})
