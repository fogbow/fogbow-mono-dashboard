from django.conf.urls.defaults import patterns  # noqa
from django.conf.urls.defaults import url  # noqa

from .views import IndexView
from openstack_dashboard.dashboards.fogbow.federated_network import views

urlpatterns = patterns('',
    url(r'^join/$', views.JoinView.as_view(), name='join'),
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^(?P<federated_network_id>.*)/members$', views.getSpecificFederatedMembers, name='members'),    
)
