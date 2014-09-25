from django.utils.translation import ugettext_lazy as _

from django.core.urlresolvers import reverse_lazy  # noqa
from django.core.urlresolvers import reverse  # noqa

from django.conf import settings
import requests
from horizon import tables

class TerminateInstance(tables.BatchAction):
    name = "terminate"
    action_present = _("Terminate")
    action_past = _("Scheduled termination of")
    data_type_singular = _("Instance")
    data_type_plural = _("Instances")
    classes = ('btn-danger', 'btn-terminate')
    success_url = reverse_lazy("horizon:fogbow:instance:index")

    def allowed(self, request, instance=None):
        return True

    def action(self, request, obj_id):
        headers = {'content-type': 'text/occi', 'X-Auth-Token' : settings.MY_TOKEN}        
        r = requests.delete( settings.MY_ENDPOINT + '/compute/' + obj_id, headers=headers)        

class InstancesTable(tables.DataTable):
    instanceId = tables.Column("instanceId", verbose_name=_("Instance ID"))

    class Meta:
        name = "instances"
        verbose_name = _("Instances")        
        table_actions = (TerminateInstance, )
        row_actions = (TerminateInstance, )
        