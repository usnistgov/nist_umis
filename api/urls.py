""" urls for the substances app """
from django.urls import path
from api import views


urlpatterns = [
    path("", views.home, name='index'),
    path("units/view/<uid>", views.unitview, name='json'),
    path("units/list/", views.unitslist, name='list'),
]
