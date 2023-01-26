""" urls for the units app """
from django.urls import path, include
from . import views


urlpatterns = [
    path("", views.home, name='homepage'),
    path("search", views.search, name='search'),
    path("units", views.index, name='index'),
    path("units/view/<uid>", views.view, name='view'),
    path('unitsystems/', include('unitsystems.urls')),
    path('quantitysystems/', include('quantitysystems.urls')),
    path('quantitykinds/', include('quantitykinds.urls')),
    path('repsystems/', include('repsystems.urls')),
    path('quantities/', include('quantities.urls')),
    path('representations/', include('representations.urls')),
    path('vectors/', include('vectors.urls')),
    path('constants/', include('constants.urls')),
]
