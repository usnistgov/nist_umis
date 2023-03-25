""" urls for the substances app """
from django.urls import path
from api import views
from units import views as uviews


urlpatterns = [
    path("", views.home, name='index'),
    path("spec", views.spec, name='spec'),
    path("units/list/", views.unitslist, name='units list'),
    path("units/view/<uid>", views.unitview, name='unit view'),
    path("units/search/<term>", views.unitsrch, name='unit search'),
    path("units/crosswalk/<sys1id>/<sys2id>", uviews.crosswalk, name='unit crosswalk'),

]
