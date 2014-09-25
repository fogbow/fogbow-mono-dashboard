from django.utils.translation import ugettext_lazy as _

from django.core.urlresolvers import reverse_lazy  # noqa
import requests
from django.conf import settings
from horizon import tables
import openstack_dashboard.dashboards.fogbow.models as fogbow_request
from horizon import messages

class TerminateRequest(tables.BatchAction):
    name = "terminate"
    action_present = _("Terminate")
    action_past = _("Scheduled termination of")
    data_type_singular = _("Request")
    data_type_plural = _("Requests")
    classes = ('btn-danger', 'btn-terminate')
#     success_url = reverse_lazy("horizon:fogbow:request:index")   

    def allowed(self, request, instance=None):
        return True

    def action(self, request, obj_id):        
        requestId = obj_id.split(':')[0]
        response = fogbow_request.doRequest('delete', '/fogbow_request/' + requestId, None)   
        if response.status_code >= 200 and response.status_code <= 204:
            messages.success(request, _('Success : %s Deleted') % requestId)
        else:
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
        