from django.utils.translation import ugettext_lazy as _
from horizon import tabs
import openstack_dashboard.models as fogbow_models
import logging

LOG = logging.getLogger(__name__)
                
NETWORK_TERM = fogbow_models.FogbowConstants.NETWORK_TERM
COMPUTE_TERM = fogbow_models.FogbowConstants.COMPUTE_TERM
STATE_TERM = fogbow_models.FogbowConstants.STATE_TERM
SHH_PUBLIC_KEY_TERM = fogbow_models.FogbowConstants.SHH_PUBLIC_KEY_TERM
CONSOLE_VNC_TERM = fogbow_models.FogbowConstants.CONSOLE_VNC_TERM
MEMORY_TERM = fogbow_models.FogbowConstants.MEMORY_TERM
CORES_TERM = fogbow_models.FogbowConstants.CORES_TERM
IMAGE_SCHEME = fogbow_models.FogbowConstants.IMAGE_SCHEME     
EXTRA_PORT_SCHEME = fogbow_models.FogbowConstants.EXTRA_PORT_SCHEME

NETWORK_VLAN = "occi.network.vlan="
NETWORK_LABEL = "occi.network.label="
NETWORK_STATE = "occi.network.state="
NETWORK_ADDRESS = "occi.network.address="
NETWORK_GATEWAY = "occi.network.gateway="
NETWORK_ALLOCATION = "occi.network.allocation="

class InstanceDetailTabInstancePanel(tabs.Tab):
    name = _("Federated Network details")
    slug = "federated_networks_details"
    template_name = ("fogbow/network/_detail_federated_network.html")

    def get_context_data(self, request):

        return null
    
def getInstancePerResponse(instanceId, response):
            
    return null
    
def normalizeAttributes(propertie, term):
    try:
        return propertie.split(term)[1].replace('=', '').replace('"', '')
    except:
        return ''                
                
class InstanceDetailTabGroupInstancePanel(tabs.TabGroup):
    slug = "federated_networks_details"
    tabs = (InstanceDetailTabInstancePanel,)
