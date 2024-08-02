""" urls for the substances app """
from django.urls import path
from constants import views


urlpatterns = [
    path("", views.index, name='index'),
    path("view/<cnid>", views.view, name='view'),
    # path("symbol/<cnid>", views.symbol, name='symbol'),
    path("alldata/<cnid>", views.alldata, name='alldata'),
    path("json/<cnid>", views.jsonout, name='json'),
]
