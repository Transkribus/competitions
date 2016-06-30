from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^logout$', views.signout, name='signout'),
    url(r'^((?P<competition_id>[0-9]+)/)?((?P<track_id>[0-9]+)/)?((?P<subtrack_id>[0-9]+)/)?$', views.competition, name='competition'),
    url(r'^(?P<competition_id>[0-9]+)/(?P<track_id>[0-9]+)/(?P<subtrack_id>[0-9]+)/submit$', views.submit, name='submit'),
    url(r'^(?P<competition_id>[0-9]+)/(?P<track_id>[0-9]+)/(?P<subtrack_id>[0-9]+)/viewresults$', views.viewresults, name='viewresults')
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url('^', include('django.contrib.auth.urls')),
]
