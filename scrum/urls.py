from django.conf.urls import patterns, include, url
from scrum.views import *
urlpatterns = patterns('',
            url('^$', view=index),
            url('callback/$', view=callback),
            url('channel/$', view=channel),
            url('display/$', view=display),
            url('logout/$',view = logout),
            url('callback/scrum/$',view = logout),

)

