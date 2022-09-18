from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse


def get_data(request, *args, **kwargs):
    data = {"sales": 100, "person": 10000}
    return JsonResponse(data)
