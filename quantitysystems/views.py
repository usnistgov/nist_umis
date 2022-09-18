from django.shortcuts import render
from units.models import *


def index(request):
    qsyss = Quantitysystems.objects.all().order_by('name')
    return render(request, "../templates/quantitysystems/index.html", {'qsyss': qsyss})


def view(request, qsid):
    qsys = Quantitysystems.objects.get(id=qsid)
    dims = qsys.dimensions_set.all().order_by('type')
    return render(request, "../templates/quantitysystems/view.html", {'qsys': qsys, 'dims': dims})
