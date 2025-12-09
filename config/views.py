""" solubility views file """
from django.shortcuts import render
from sds.serializers import *
from django.utils import timezone
from django.shortcuts import redirect


def index(request):
    """ front page of the website """
    return render(request, "home.html")
