"""umisconfig URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('units.urls')),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('calculations/', include('calculations.urls')),
    path('domains/', include('domains.urls')),
    path('unitsystems/', include('unitsystems.urls')),
    path('quantitysystems/', include('quantitysystems.urls')),
    path('quantitykinds/', include('quantitykinds.urls')),
    path('repsystems/', include('repsystems.urls')),
    path('quantities/', include('quantities.urls')),
    path('representations/', include('representations.urls')),
    path('vectors/', include('vectors.urls')),
    path('constants/', include('constants.urls')),
]
