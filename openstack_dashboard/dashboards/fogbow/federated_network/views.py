from django.utils.translation import ugettext_lazy as _  # noqa
from horizon import views
from horizon import tables
from horizon import forms
from horizon import tabs
import logging

from django.core.urlresolvers import reverse_lazy 
from django.utils.translation import ugettext_lazy as _

from openstack_dashboard.dashboards.fogbow.federated_network \
    import tabs as project_tabs
from openstack_dashboard.dashboards.fogbow.federated_network \
    import tables as project_tables
from openstack_dashboard.dashboards.fogbow.federated_network \
    import models as project_models    
import openstack_dashboard.models as fogbow_models
from openstack_dashboard.dashboards.fogbow.federated_network.models import FederatedNetwork
from openstack_dashboard.dashboards.fogbow.federated_network.forms import JoinMember
from django.http import HttpResponse
import json

LOG = logging.getLogger(__name__)

class IndexView(tables.DataTableView):
    table_class = project_tables.InstancesTable
    template_name = 'fogbow/federated_network/index.html'

    def get_data(self):
        fed_networks = []

        fed_network_one = {'id' : '10', 'federatedNetworkId' : 'abc', 'cidr': '10.0.0.0/24', 'providers' : 'A, B, C'}
        fed_network_two = {'id' : '20', 'federatedNetworkId' : 'abc', 'cidr': '188.0.0.0/24', 'providers' : 'A, B, C'}
        fed_networks.append(FederatedNetwork(fed_network_one))
        fed_networks.append(FederatedNetwork(fed_network_two))     
            
        return fed_networks

def getSpecificFederatedMembers(request, federated_network_id):
        data = []
        data.append('catch-all.manager.naf.lsd.ufcg.edu.br')
        data.append('manager.naf.ufscar.br')
        return HttpResponse(json.dumps(data))

class DetailViewInstance(tabs.TabView):
    tab_group_class = project_tabs.InstanceDetailTabGroupInstancePanel
    template_name = 'fogbow/federated_network/detail.html'     
    
class JoinView(forms.ModalFormView):
    form_class = JoinMember
    template_name = 'fogbow/federated_network/create.html'
    success_url = reverse_lazy('horizon:fogbow:index')
        