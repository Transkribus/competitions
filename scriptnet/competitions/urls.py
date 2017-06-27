from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^tokens/(?P<token_id>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/$', views.activate, name='activate'),
    url(r'^tokens/react/(?P<token_id>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/$', views.reactivate, name='reactivate'),
    url(r'^logout/$', views.signout, name='signout'),
    url(r'^~(?P<competition_name>.+)/$', views.competition_alias, name='competition_alias'),
    url(r'^(?P<competition_id>[0-9]+)/mymethods/$', views.methodlist, name='methodlist'),    
    url(r'^(?P<competition_id>[0-9]+)/scoreboard/$', views.scoreboard, name='scoreboard'),
    url(r'^(?:(?P<competition_id>[0-9]+)/?)(?:/(?P<track_id>[0-9]+))?(?:/(?P<subtrack_id>[0-9]+))?/$', views.competition, name='competition'),
    url(r'^(?P<competition_id>[0-9]+)/(?P<track_id>[0-9]+)/(?P<subtrack_id>[0-9]+)/submit/$', views.submit, name='submit'),
    url(r'^(?P<competition_id>[0-9]+)/(?:(?P<track_id>[0-9]+)/)?(?:(?P<subtrack_id>[0-9]+)/)?viewresults/$', views.viewresults, name='viewresults'),
    url(r'^$', views.index, name='index'),    
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url('^', include('django.contrib.auth.urls')),
]