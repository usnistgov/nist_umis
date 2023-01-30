""" view file for the repsystem app """
from django.shortcuts import render
from django.http import JsonResponse
from units.models import *


def index(request):
    """ get a list of representation systems """
    rsyss = Repsystems.objects.all().order_by('name').exclude(status='ignore')
    return render(request, "../templates/repsystems/index.html", {'rsyss': rsyss})


def view(request, rsid):
    """ get data about a representation system and the unit representations in the db """
    rsys = Repsystems.objects.get(id=rsid)
    reps = rsys.representations_set.all()
    return render(request, "../templates/repsystems/view.html", {'rsys': rsys, 'reps': reps})


def units(request, rsid):
    """ get a list of representations unit system to send to a browser via ajax """
    reps = Representations.objects.filter(repsystem_id=rsid).order_by('unit__name')
    data = {}
    for rep in reps:
        name = rep.unit.name
        uid = rep.unit.id
        sym = rep.strng.string
        data.update({uid: name + ':' + sym})
    return JsonResponse(data, safe=False)
