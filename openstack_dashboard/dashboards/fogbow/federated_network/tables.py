from django.utils.translation import ugettext_lazy as _

from django.core.urlresolvers import reverse_lazy  # noqa
from django.core.urlresolvers import reverse  # noqa

from django.conf import settings
import requests
from horizon import tables
from horizon import messages

import openstack_dashboard.models as fogbow_models

FEDERATED_NETWORK_TERM = fogbow_models.FogbowConstants.FEDERATED_NETWORK_TERM

class TerminateInstance(tables.BatchAction):
    name = "remove"
    action_present = _("Remove")
    action_past = _("Removed")
    data_type_singular = ""
    data_type_plural = _("Federated Networls")
    classes = ('btn-danger', 'btn-terminate')
    success_url = reverse_lazy("horizon:fogbow:federated_network:index")

    def allowed(self, request, instance=None):
        return True

    def action(self, request, obj_id):
        requestId = obj_id.split(':')[0]
        response = fogbow_models.doRequest('delete', FEDERATED_NETWORK_TERM + requestId, None, request)   
        if fogbow_models.isResponseOk(response.text) == False:
            messages.error(request, _('Is was not possible to delete : %s') % requestId)
        
class JoinInstance(tables.BatchAction):
    name = "join"
    action_present = _("Join provider")
    action_past = _("Join provider")
    data_type_singular = ""
    data_type_plural = ""
    classes = ('btn-info', 'btn-terminate')
    success_url = reverse_lazy("horizon:fogbow:federated_network:index")

    def allowed(self, request, instance=None):
        return True

    def action(self, request, obj_id):
        self.current_past_action = 0        

class JoinMember(tables.LinkAction):
    name = 'join'
    verbose_name = _('Join member')
    url = 'horizon:fogbow:federated_network:join'
    classes = ('ajax-modal', 'btn-create')

def get_instance_id(request):
    if 'null' not in request.federatedNetworkId:
        return request.federatedNetworkId 
    else:
        return '-'

class InstancesFilterAction(tables.FilterAction):
    def filter(self, table, federated_networks, filter_string):
        q = filter_string.lower()
        return [federated_network for federated_network in federated_networks
                if q in federated_network.name.lower()]

class InstancesTable(tables.DataTable):
    id = tables.Column(get_instance_id, verbose_name=_("Federated Network ID"))
    label = tables.Column('label', verbose_name=_('Label'))
    cidr = tables.Column('cidr', verbose_name=_('CIDR'))
    members = tables.Column('members', verbose_name=_('Members'))

    class Meta:
        name = "federated_network"
        verbose_name = _("Federated Networks")        
        table_actions = (TerminateInstance, InstancesFilterAction, JoinMember)
        row_actions = (TerminateInstance,)
        