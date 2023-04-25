from django.shortcuts import render
from units.models import *


def index(request):
    """ present an overview page about the system in the sds """
    vectors = Dimensionvectors.objects.all().values('id', 'name').order_by('name')
    return render(request, "../templates/vectors/index.html", {'vectors': vectors})


def view(request, dvid):
    vector = Dimensionvectors.objects.get(id=dvid)
    qkinds = vector.quantitykinds_set.all()
    qsys = vector.quantitysystem
    return render(request, "../templates/vectors/view.html", {'vector': vector, 'qkinds': qkinds, 'qsys': qsys})
