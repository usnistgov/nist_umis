from django.shortcuts import render
from units.models import *


def index(request):
    qkinds = Quantitykinds.objects.all().order_by('name')
    return render(request, "../templates/quantitykinds/index.html", {'qkinds': qkinds})


def view(request, qkid):
    qkind = Quantitykinds.objects.get(id=qkid)
    quants = qkind.quantities_set.all()
    return render(request, "../templates/quantitykinds/view.html", {'qkind': qkind, 'quants': quants})
