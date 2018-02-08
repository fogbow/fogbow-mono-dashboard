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
import re

LOG = logging.getLogger(__name__)

FEDERATED_NETWORK_TERM = fogbow_models.FogbowConstants.FEDERATED_NETWORK_TERM
FEDERATED_NETWORK_WITH_VERBOSE = fogbow_models.FogbowConstants.FEDERATED_NETWORK_WITH_VERBOSE
X_OCCI_LOCATION = fogbow_models.FogbowConstants.X_OCCI_LOCATION
FEDERATED_NETWORK_LABEL = fogbow_models.FogbowConstants.FEDERATED_NETWORK_LABEL
FEDERATED_NETWORK_CIDR = fogbow_models.FogbowConstants.FEDERATED_NETWORK_CIDR
FEDERATED_NETWORK_MEMBERS = fogbow_models.FogbowConstants.FEDERATED_NETWORK_MEMBERS

class IndexView(tables.DataTableView):
    table_class = project_tables.InstancesTable
    template_name = 'fogbow/federated_network/index.html'

    def get_data(self):
        response = fogbow_models.doRequest('get', FEDERATED_NETWORK_WITH_VERBOSE, None, self.request)
        if response is None:
            return []
        elif response.status_code is None or response.status_code >= 400:
            LOG.debug("Response from Federated Network was " + str(response.status_code))
            return []
        else:
            return self.getFederatedNetworkList(response.text)

    def getFederatedNetworkList(self, responseStr):
        federatedList = []
        fragments = responseStr.split("\n")
        for frag in fragments:
            federated = {}
            LOG.info(frag)
            try:
                federated["id"] = re.search(FEDERATED_NETWORK_TERM+"([0-9a-fA-F\\-]*)", frag).group(1)
                federated["federatedNetworkId"] = re.search(FEDERATED_NETWORK_TERM+"([0-9a-fA-F\\-]*)", frag).group(1)
                federated["label"] = re.search(FEDERATED_NETWORK_LABEL + "=([a-z A-Z]*)", frag).group(1)
                federated["cidr"] = re.search(FEDERATED_NETWORK_CIDR + "=([0-9\\./]*)", frag).group(1)
                federated["members"] = re.search(FEDERATED_NETWORK_MEMBERS + "=([ ,a-zA-Z\\.]*)", frag).group(1)
                LOG.info(FederatedNetwork(federated))
                federatedList.append(FederatedNetwork(federated))
            except Exception:
                LOG.error("Malformed response for Federated Resource")
        LOG.info(federatedList)
        return federatedList

    def normalizeAttribute(self, propertie):
        return propertie.replace(X_OCCI_LOCATION, '')

    def getInstances(self, request):
        self.request = request
        return self.get_data()

def getSpecificFederatedMembers(request, federated_network_id):
    response = fogbow_models.doRequest('get', FEDERATED_NETWORK_TERM + federated_network_id, None, request)
    data = []
    try:
        members = re.search(FEDERATED_NETWORK_MEMBERS+"=([ ,a-zA-Z\\.]*)", response.text).group(1)
        for m in members.split(","):
            data.append(m.trim())
    except Exception:
        LOG.error("Malformed response for Federated Resource with id")
    return HttpResponse(json.dumps(data))

class DetailViewInstance(tabs.TabView):
    tab_group_class = project_tabs.InstanceDetailTabGroupInstancePanel
    template_name = 'fogbow/federated_network/detail.html'     
    
class JoinView(forms.ModalFormView):
    form_class = JoinMember
    template_name = 'fogbow/federated_network/create.html'
    success_url = reverse_lazy('horizon:fogbow:index')
        