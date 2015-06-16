from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^revisar', views.revisar, name='revisar'),
    url(r'^descargar', views.descargar, name='descargar'),
    url(r'^vote', views.vote, name='vote'),
    url(r'^$', views.index, name='index'),
]


