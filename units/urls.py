""" urls for the units app """
from django.urls import path, include
from . import views


urlpatterns = [
    path("", views.home, name='homepage'),
    path("search", views.search, name='search'),
    path("units", views.index, name='index'),
    path("units/unitimport/", views.unitimport, name='import'),
    path("units/crosswalk/", views.crosswalk, name='crosswalk'),
    path("units/crosswalk/<sys1id>/<sys2id>", views.crosswalk, name='crosswalk'),
    path("units/view/<uid>", views.view, name='view'),
]
