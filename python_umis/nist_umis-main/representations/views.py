from django.shortcuts import render
from units.models import *


def index(request):
    data = Representations.objects.all().order_by('unit__name')
    units = {}
    for rep in data:
        repst = rep.strng.string
        repid = rep.id
        unit = rep.unit.name
        if unit not in units.keys():
            units.update({unit: {'reps': []}})
        rep = {'id': repid, 'strng': repst}
        # group representations by rep string (TODO)

        units[unit]['reps'].append(rep)
    return render(request, "../templates/representations/index.html", {'units': units})


def view(request, rid):
    rep = Representations.objects.get(id=rid)
    encs = Encodings.objects.filter(strng__representations__id=rid)
    return render(request, "../templates/representations/view.html", {'rep': rep, 'units': encs})
