""" views for the units app """
from django.shortcuts import render, redirect
from units.models import *
from django.core.serializers import serialize
from django.http import JsonResponse
import json


def home(request):
    """ main page for the API """
    return render(request, "../templates/api/home.html")


def units(request, uid=None):
    """ API endpoint for units """
    if uid:
        opts = Units.objects.all().values_list('name', flat=True)
        if uid not in opts:
            if uid.isnumeric():
                try:
                    uid = Units.objects.get(id=uid).name
                    return redirect('/api/units/' + uid)
                except Prefixes.DoesNotExist:
                    return redirect('/')
            elif isinstance(uid, str):
                try:
                    uid = Units.objects.get(name=uid.lower()).name
                    return redirect('/api/units/' + uid)
                except Prefixes.DoesNotExist:
                    return redirect('/')

        unit = Units.objects.filter(name=uid)
        sdata = serialize("json", unit)
        data = json.loads(sdata)
        # TODO: output needs work...
        return JsonResponse(data[0]['fields'], safe=False)
    else:
        return redirect('/api/home')
