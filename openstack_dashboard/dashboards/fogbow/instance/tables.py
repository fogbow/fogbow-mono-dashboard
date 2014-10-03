from django.utils.translation import ugettext_lazy as _

from django.core.urlresolvers import reverse_lazy  # noqa
from django.core.urlresolvers import reverse  # noqa

from django.conf import settings
import requests
from horizon import tables

import openstack_dashboard.models as fogbow_request

COMPUTE_TERM = '/compute/'

class TerminateInstance(tables.BatchAction):
    name = "terminate"
    action_present = _("Terminate")
    action_past = _("Terminated")
    data_type_singular = _("Instance")
    data_type_plural = _("Instances")
    classes = ('btn-danger', 'btn-terminate')
    success_url = reverse_lazy("horizon:fogbow:instance:index")

    def allowed(self, request, instance=None):
        return True

    def action(self, request, obj_id):
        self.current_past_action = 0                
        r = fogbow_request.doRequest('delete',COMPUTE_TERM + obj_id, None,
                                      request.session.get('token','').id)        

class InstancesTable(tables.DataTable):
    instanceId = tables.Column("instanceId", verbose_name=_("Instance ID"))

    class Meta:
        name = "instances"
        verbose_name = _("Instances")        
        table_actions = (TerminateInstance, )
        row_actions = (TerminateInstance, )
        