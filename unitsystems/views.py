""" django view file for units """
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from units.models import *


def index(request):
    """ view a list of units """
    syss = Unitsystems.objects.all().order_by('name')
    return render(request, "../templates/unitsystems/index.html", {'syss': syss})


def view(request, usid):
    """ view data about a specific unit """
    sys, units = None, None
    try:
        sys = Unitsystems.objects.get(id=usid)
        units = sys.units_set.all()
    except ObjectDoesNotExist:
        return redirect('/')
    return render(request, "../templates/unitsystems/view.html", {'sys': sys, 'units': units})
