""" urls for the substances app """
from django.urls import path
from charts import views


urlpatterns = [
    path("api", views.get_data, name='data')
]
