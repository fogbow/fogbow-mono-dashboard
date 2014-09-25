from django.conf.urls.defaults import patterns  # noqa
from django.conf.urls.defaults import url  # noqa

from openstack_dashboard.dashboards.fogbow.request import views

urlpatterns = patterns('',
    url(r'^create/$', views.CreateView.as_view(), name='create'),
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<instance_id>[^/]+)/details$', views.DetailView.as_view(), name='detail'),
)
