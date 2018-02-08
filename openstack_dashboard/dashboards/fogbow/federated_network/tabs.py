from django.utils.translation import ugettext_lazy as _
from horizon import tabs
import openstack_dashboard.models as fogbow_models
import logging
import re

LOG = logging.getLogger(__name__)

FEDERATED_NETWORK_TERM = fogbow_models.FogbowConstants.FEDERATED_NETWORK_TERM
FEDERATED_NETWORK_LABEL = fogbow_models.FogbowConstants.FEDERATED_NETWORK_LABEL
FEDERATED_NETWORK_CIDR = fogbow_models.FogbowConstants.FEDERATED_NETWORK_CIDR
FEDERATED_NETWORK_MEMBERS = fogbow_models.FogbowConstants.FEDERATED_NETWORK_MEMBERS

class InstanceDetailTabInstancePanel(tabs.Tab):
    name = _("Federated Network details")
    slug = "federated_networks_details"
    template_name = ("fogbow/federated_network/_detail_instance.html")

    def get_context_data(self, request):
        instanceId = self.tab_group.kwargs['instance_id']
        instanceId = instanceId[0:instanceId.find("@")]
        response = fogbow_models.doRequest('get', FEDERATED_NETWORK_TERM  + instanceId, None, request)   

        instance = None
        try:
            instance = getInstancePerResponse(instanceId, response.text)
        except Exception:
            instance = {'federatedNetworkId': '-' , 'label': '-', 'cidr': '-', 'members': '-'}
        return {'instance' : instance}
    
def getInstancePerResponse(instanceId, response):
    federated = {}
    federated["id"] = "-"
    federated["federatedNetworkId"] = "-"
    federated["label"] = "-"
    federated["cidr"] = "-"
    federated["members"] = "-"
    try:
        LOG.error(response)
        federated["id"] = re.search(FEDERATED_NETWORK_TERM+"([0-9a-fA-F\\-]*)", response).group(1)
        federated["federatedNetworkId"] = re.search(FEDERATED_NETWORK_TERM+"([0-9a-fA-F\\-]*)", response).group(1)
        federated["label"] = re.search(FEDERATED_NETWORK_LABEL + "=([a-z A-Z]*)", response).group(1)
        federated["cidr"] = re.search(FEDERATED_NETWORK_CIDR + "=([0-9\\./]*)", response).group(1)
        federated["members"] = re.search(FEDERATED_NETWORK_MEMBERS + "=([ ,a-zA-Z\\.]*)", response).group(1)
    except Exception as error:
        LOG.error("Malformed response for Federated Resource")
        LOG.error(error)
    return federated
    
def normalizeAttributes(propertie, term):
    try:
        return propertie.split(term)[1].replace('=', '').replace('"', '')
    except:
        return ''                
                
class InstanceDetailTabGroupInstancePanel(tabs.TabGroup):
    slug = "federated_networks_details"
    tabs = (InstanceDetailTabInstancePanel,)
