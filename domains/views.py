""" view file for the quantitites app """
from django.shortcuts import render
from units.models import *


def index(request):
    """ show a list of quantities """
    doms = Domains.objects.all().order_by('title')
    return render(request, "../templates/domains/index.html", {'doms': doms})
