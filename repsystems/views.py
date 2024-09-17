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
    if rsid.isdigit():
        rsys = Repsystems.objects.get(id=rsid)
    elif type(rsid) is str:
        rsys = Repsystems.objects.get(abbrev=rsid)
    else:
        rsys = None
    if rsys is None:
        return render(request, '/')
    port = request.META['SERVER_PORT']
    reps = rsys.representations_set.all().order_by('unit__name')
    return render(request, "../templates/repsystems/view.html", {'rsys': rsys, 'reps': reps, 'port': port})


def units(request, rsid):
    """ get a list of representations unit system to send to a browser via ajax """
    reps = Representations.objects.filter(repsystem_id=rsid, url_endpoint='yes').order_by('unit__name')
    data = {}
    for rep in reps:
        name = rep.unit.name
        uid = rep.unit.id
        sym = rep.strng.string
        data.update({uid: name + ':' + sym})
    return JsonResponse(data, safe=False)


def cross(request, rsid1, rsid2):
    """ get a list of representations unit system to send to a browser via ajax """
    reps1 = Representations.objects.filter(repsystem_id=rsid1, url_endpoint='yes').order_by('unit__name')
    reps2 = Representations.objects.filter(repsystem_id=rsid2, url_endpoint='yes').order_by('unit__name')
    rep2list = {}
    for rep2 in reps2:
        rep2list.update({rep2.unit.id: rep2.strng.string})

    # add entries in reps1
    data = {}
    for rep1 in reps1:
        uid = rep1.unit.id
        name = rep1.unit.name
        rep1 = rep1.strng.string
        if uid in rep2list.keys():
            rep2 = rep2list[uid]
            del rep2list[uid]
        else:
            rep2 = 'no equivalent'
        data.update({name: rep1 + ':' + rep2})
    # add entries in reps2 that were not matched in reps1
    for uid, rep2str in rep2list.items():
        for rep2 in reps2:
            if rep2.strng.string == rep2str:
                data.update({rep2.unit.name: 'no equivalent:' + rep2str})
    # sort by name
    data = dict(sorted(data.items()))

    return JsonResponse(data, safe=False)
