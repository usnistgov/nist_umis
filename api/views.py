""" views for the units app """
from django.shortcuts import render, redirect
from units.models import *
from django.core.serializers import serialize
from django.http import JsonResponse
import datetime
import json


def home(request):
    """ redirect to the OpenAPI page on Swaggerhub """
    return redirect("https://app.swaggerhub.com/apis-docs/stuchalk/nist-umis/1.0.0")


def unitview(request, uid=None):
    """ API endpoint for units """
    if not uid:
        return redirect('/api/home')
    opts = Units.objects.all().values_list('name', flat=True)
    if uid not in opts:
        if uid.isnumeric():
            try:
                uid = Units.objects.get(id=uid).name
                return redirect('/api/units/view/' + uid)
            except Prefixes.DoesNotExist:
                return redirect('/')
        elif isinstance(uid, str):
            try:
                uid = Units.objects.get(name=uid.lower()).name
                return redirect('/api/units/view/' + uid)
            except Prefixes.DoesNotExist:
                return redirect('/')

    unit = Units.objects.filter(name=uid)[0]
    reps = Representations.objects.filter(unit_id=unit.id)
    site = "http://127.0.0.1:8000/"
    output = {"@context": ["http://127.0.0.1:8000/files/contexts/umis.jsonld", {
        "xsd": "https://www.w3.org/2001/XMLSchema#",
        "ncit": "http://purl.obolibrary.org/obo/ncit.owl",
        "qkind": "http://www.qudt.org/schema/qudt/"
    }, {
        "@base": "http://127.0.0.1:8000/api/units/list/"
    }]}
    output.update({"@id": "http://127.0.0.1:8000/api/units/view/" + uid})
    output.update({"generatedAt": datetime.datetime.now()})
    output.update({"version": 0.6})
    graph = {"@id": "http://127.0.0.1:8000/api/units/view/" + uid}
    graph.update({"@type": "ncit:NCIT_C25709"})
    graph.update({"name": unit.name})
    graph.update({"description": unit.description})
    graph.update({"url": "http://127.0.0.1:8000/api/units/view/" + uid})
    graph.update({"definitionurl": unit.url})
    graph.update({"unittype": unit.type})
    graph.update({"unitshortcode": unit.shortcode})
    graph.update({"apiversion": "0.2"})
    graph.update({"timestamp": datetime.datetime.now()})
    output.update({"@graph": graph})
    rs = []
    for rep in reps:
        r = {'@id': "http://127.0.0.1:8000/representations/view/" + uid}
        r.update({"@type": "ncit:NCIT_C67045"})
        r.update({"repsystem": rep.repsystem.name})
        r.update({"string": rep.strng.string})
        rs.append(r)
    output.update({"representations": rs})
    return JsonResponse(output, safe=False)


def unitslist(request):
    data = Units.objects.all()
    site = "http://127.0.0.1:8000/"
    output = {"@context": ["http://127.0.0.1:8000/files/contexts/umis.jsonld", {
      "xsd": "https://www.w3.org/2001/XMLSchema#",
      "ncit": "http://purl.obolibrary.org/obo/ncit.owl",
      "qkind": "http://www.qudt.org/schema/qudt/"
    }, {
      "@base": "http://127.0.0.1:8000/api/units/list/"
    }]}
    output.update({"@id": "http://127.0.0.1:8000/api/units/list/"})
    output.update({"generatedAt": datetime.datetime.now()})
    output.update({"version": 0.6})
    graph = {"@id": "http://127.0.0.1:8000/api/units/list/"}
    graph.update({"@type": "ncit:NCIT_C43432"})
    graph.update({"uid": "umis:units:list:0.6"})
    graph.update({"title": "List of SI Units"})
    graph.update({"description": "List of SI units (and related) in the UMIS database"})
    graph.update({"timestamp": datetime.datetime.now()})
    graph.update({"apiurl": "http://127.0.0.1:8000/api/units/list/"})
    graph.update({"apiversion": "0.2"})
    output.update({"@graph": graph})
    units = []
    for datum in data:
        u = {"@id": "unit/" + str(datum.id) + "/"}
        u.update({"@type": "ncit:NCIT_C25709"})
        u.update({"name": datum.name})
        u.update({"url": site + "units/view/" + str(datum.id)})
        units.append(u)
    output.update({'units': units})
    return JsonResponse(output, safe=False)
