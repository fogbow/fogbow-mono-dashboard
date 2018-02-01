from django.utils.translation import ugettext_lazy as _

from django.core.urlresolvers import reverse_lazy  # noqa
from django.core.urlresolvers import reverse  # noqa

from django.conf import settings
import requests
from horizon import tables
from horizon import messages

import openstack_dashboard.models as fogbow_models
import openstack_dashboard.dashboards.fogbow.instance.tables as tableInstanceDashboard

NETWORK_TERM = fogbow_models.FogbowConstants.NETWORK_TERM
COMPUTE_TERM = '/compute/'

class TerminateInstance(tables.BatchAction):
    name = "terminate"
    action_present = _("Terminate")
    action_past = _("Terminated")
    data_type_singular = _("federated_network")
    data_type_plural = _("federated_networks")
    classes = ('btn-danger', 'btn-terminate')
    success_url = reverse_lazy("horizon:fogbow:federated_network:index")

    def allowed(self, request, instance=None):
        return True

    def action(self, request, obj_id):
        self.current_past_action = 0        
        response = fogbow_models.doRequest('delete', NETWORK_TERM + obj_id, None, request)
        if response == None or fogbow_models.isResponseOk(response.text) == False:
            messages.error(request, _('Is was not possible to delete : %s') % obj_id)          
            tableInstanceDashboard.checkAttachmentAssociateError(request, response.text)

def get_instance_id(request):
    if 'null' not in request.federatedNetworkId:
        return request.federatedNetworkId 
    else:
        return '-'

class InstancesFilterAction(tables.FilterAction):

    def filter(self, table, instances, filter_string):
        q = filter_string.lower()
        return [instance for instance in instances
                if q in instance.name.lower()]

class InstancesTable(tables.DataTable):
    id = tables.Column(get_instance_id, verbose_name=_("Federated Network ID"))
    allowed = tables.Column('allowed', verbose_name=_('Connections Allowed'))
    providers = tables.Column('providers', verbose_name=_('Providers'))

    class Meta:
        name = "federated_network"
        verbose_name = _("Federated Networks")        
        table_actions = (TerminateInstance, InstancesFilterAction)
        row_actions = (TerminateInstance, )
        