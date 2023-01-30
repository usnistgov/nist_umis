""" urls for the substances app """
from django.urls import path
from api import views
from units import views as uviews


urlpatterns = [
    path("", views.home, name='index'),
    path("units/view/<uid>", views.unitview, name='json'),
    path("units/list/", views.unitslist, name='list'),
    path("units/crosswalk/<sys1id>/<sys2id>", uviews.crosswalk, name='crosswalk'),
]
