""" urls for the substances app """
from django.urls import path
from repsystems import views


urlpatterns = [
    path("", views.index, name='index'),
    path("view/<rsid>", views.view, name='view'),
    path("units/<rsid>", views.units, name='units'),
    path("cross/<rsid1>/<rsid2>", views.cross, name='crosswalk'),
]
