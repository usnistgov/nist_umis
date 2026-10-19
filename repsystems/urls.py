""" urls for the substances app """
from django.urls import path
from repsystems import views


urlpatterns = [
    path("", views.index, name='repsystem index'),
    path("view/<rsid>", views.view, name='repsystem view'),
    path("units/<rsid>", views.units, name='repsystem units'),
    path("cross/<rsid1>/<rsid2>", views.cross, name='repsystem crosswalk'),
]
