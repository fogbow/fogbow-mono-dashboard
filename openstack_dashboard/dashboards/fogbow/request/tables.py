from django.utils.translation import ugettext_lazy as _

from horizon import tables
import openstack_dashboard.models as fogbow_models
from horizon import messages

REQUEST_TERM = fogbow_models.FogbowConstants.REQUEST_TERM

class TerminateRequest(tables.BatchAction):
    name = 'terminate'
    action_present = _('Terminate')
    action_past = _('Terminated')
    data_type_singular = _('Request')
    data_type_plural = _('Requests')
    classes = ('btn-danger', 'btn-terminate')

    def allowed(self, request, instance=None):
        return True

    def action(self, request, obj_id):        
        requestId = obj_id.split(':')[0]
        response = fogbow_models.doRequest('delete', REQUEST_TERM + requestId, None, request)   
        if fogbow_models.isResponseOk(response.text) == False:
            messages.error(request, _('Is was not possible to delete : %s') % requestId)      

class CreateRequest(tables.LinkAction):
    name = 'create'
    verbose_name = _('Create Request')
    url = 'horizon:fogbow:request:create'
    classes = ('ajax-modal', 'btn-create')
    
def get_instance_id(request):
    if 'null' not in request.instanceId:
        return request.instanceId 
    else:
        return '-'

class RequestsFilterAction(tables.FilterAction):

    def filter(self, table, requests, filter_string):
        q = filter_string.lower()
        return [request for request in requests
                if q in request.name.lower()]

class RequestsTable(tables.DataTable):
    requestId = tables.Column('requestId', verbose_name=_('Request ID'))
    state = tables.Column('state', verbose_name=_('State'))
    type = tables.Column('type', verbose_name=_('Type'))
    instanceId = tables.Column(get_instance_id, link=('horizon:fogbow:request:detail'),
                                verbose_name=_('Instance ID'))    

    class Meta:
        name = 'request'
        verbose_name = _('Requests')        
        table_actions = (CreateRequest, TerminateRequest,  RequestsFilterAction)
        row_actions = (TerminateRequest, )
        