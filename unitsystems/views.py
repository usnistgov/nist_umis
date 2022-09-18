from django.shortcuts import render
from units.models import *


def index(request):
    syss = Unitsystems.objects.all().order_by('name')
    return render(request, "../templates/unitsystems/index.html", {'syss': syss})


def view(request, usid):
    sys = Unitsystems.objects.get(id=usid)
    units = sys.units_set.all()
    return render(request, "../templates/unitsystems/view.html", {'sys': sys, 'units': units})
