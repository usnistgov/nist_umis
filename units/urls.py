""" urls for the units app """
from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name='homepage'),
    path("search", views.search, name='search'),
    path("units/", views.oldindex, name='index'),
    path("units/index", views.oldindex, name='index'),
    path("units/view/<uid>", views.oldview, name='view'),
    path("units/unitimport/", views.unitimport, name='import'),
    path("units/crosswalk/", views.crosswalk, name='crosswalk'),
    path("units/crosswalk/<sys1id>/<sys2id>", views.crosswalk, name='crosswalk'),
]
