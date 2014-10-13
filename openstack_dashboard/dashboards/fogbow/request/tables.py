from django.utils.translation import ugettext_lazy as _

from django.core.urlresolvers import reverse_lazy  # noqa
import requests
from django.conf import settings
from horizon import tables
import openstack_dashboard.models as fogbow_request
from horizon import messages

REQUEST_TERM = '/fogbow_request/'

class TerminateRequest(tables.BatchAction):
    name = "terminate"
    action_present = _("Terminate")
    action_past = _("Terminated")
    data_type_singular = _("Request")
    data_type_plural = _("Requests")
    classes = ('btn-danger', 'btn-terminate')

    def allowed(self, request, instance=None):
        return True

    def action(self, request, obj_id):        
        requestId = obj_id.split(':')[0]
        response = fogbow_request.doRequest('delete', REQUEST_TERM + requestId, None, request)   
        if response.status_code < 200 and response.status_code > 204:
            messages.error(request, _('Error _ %s') % requestId)            

class CreateRequest(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Request")
    url = "horizon:fogbow:request:create"
    classes = ("ajax-modal", "btn-create")
    
def get_instance_id(request):
    value = request.instanceId
    if 'null' not in value:
        return value 
    else:
        return '-'

class RequestsTable(tables.DataTable):
    requestId = tables.Column("requestId", verbose_name=_("Request ID"))
    state = tables.Column("state", verbose_name=_("State"))
    type = tables.Column("type", verbose_name=_("Type"))
    instanceId = tables.Column(get_instance_id, link=("horizon:fogbow:request:detail"), verbose_name=_("Instance ID"))    

    class Meta:
        name = "request"
        verbose_name = _("Requests")        
        table_actions = (CreateRequest, TerminateRequest,)
        row_actions = (TerminateRequest, )
        