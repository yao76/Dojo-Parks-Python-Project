from django.conf.urls import url, include
from django.contrib import admin
from . import views
from apps.login.urls import urlpatterns

urlpatterns = [
    url(r'^infopage/dark/(?P<parkid>\d+)$', views.darkparkinfo),
    url(r'^infopage/(?P<parkid>\d+)$', views.parkinfo),
    url(r'^darkmode$', views.darkmode),
    url(r'^create$', views.create),
    url(r'^createdark$', views.createdark),
    url(r'^remove/(?P<parkid>\d+)$', views.removePark),
    url(r'^remove/dark/(?P<parkid>\d+)$', views.removeParkDark),
    url(r'^apis/(?P<lat>-?[0-9]\d*(\.\d+)?)/(?P<long>-?[0-9]\d*(\.\d+)?)$', views.apis),
    url(r'^$', views.index),
    ]
