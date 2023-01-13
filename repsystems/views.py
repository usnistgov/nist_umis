from django.shortcuts import render
from units.models import *


def index(request):
    rsyss = Repsystems.objects.all().order_by('name').exclude(status='ignore')
    return render(request, "../templates/repsystems/index.html", {'rsyss': rsyss})


def view(request, rsid):
    rsys = Repsystems.objects.get(id=rsid)
    reps = rsys.representations_set.all()
    return render(request, "../templates/repsystems/view.html", {'rsys': rsys, 'reps': reps})
