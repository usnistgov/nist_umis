""" quantitysystem view functions """
from django.shortcuts import render
from units.models import *


def index(request):
    """ function to present the index page for all quantity systems """
    qsyss = Quantitysystems.objects.all().order_by('name')
    return render(request, "../templates/quantitysystems/index.html", {'qsyss': qsyss})


def view(request, qsid):
    """ function to present the information about a quantity systems """
    qsys = Quantitysystems.objects.get(id=qsid)
    dims = qsys.dimensions_set.all().order_by('type')
    quants = qsys.quantities_set.all().order_by('name')
    return render(request, "../templates/quantitysystems/view.html", {'qsys': qsys, 'dims': dims, 'quants': quants})
