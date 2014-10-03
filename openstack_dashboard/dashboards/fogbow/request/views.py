from horizon import views

import requests
from horizon import tables
from horizon import tabs

from django.core.urlresolvers import reverse_lazy  # noqa
from django.utils.translation import ugettext_lazy as _  # noqa

from horizon import forms
from horizon import exceptions

from openstack_dashboard.dashboards.fogbow.request \
    import tabs as project_tabs
from openstack_dashboard.dashboards.fogbow.request \
    import tables as project_tables
from openstack_dashboard.dashboards.fogbow.request \
    import models as project_models    
from openstack_dashboard.dashboards.fogbow.request.forms import CreateRequest
from openstack_dashboard.dashboards.fogbow.request.models import Request
import openstack_dashboard.models as fogbow_request

REQUEST_TERM = '/fogbow_request?verbose=true'
STATE_TERM = 'org.fogbowcloud.request.state'
TYPE_TERM = 'org.fogbowcloud.request.type'
INSTANCE_ID_TERM = 'org.fogbowcloud.request.instance-id'

class IndexView(tables.DataTableView):
    table_class = project_tables.RequestsTable
    template_name = 'fogbow/request/index.html'
    
    def has_more_data(self, table):
        return self._more

    def get_data(self):             
        response = fogbow_request.doRequest('get', REQUEST_TERM, None,
                                             self.request.session.get('token','').id)      
        
        listRequests = self.getRequestsList(response.text)        
        self._more = False
        
        return listRequests

    def getRequestsList(self, responseStr):
        listRequests = []
        propertiesRequests = responseStr.split('\n')
        for propertiesOneRequest in propertiesRequests:
            propertiesOneRequest = propertiesOneRequest.split(REQUEST_TERM + '/')
            if len(propertiesOneRequest) > 1:
                propertiesOneRequest = propertiesOneRequest[1]                
                properties = propertiesOneRequest.split(';')
                
                state, type, instanceId = '-', '-', '-'
                for propertie in properties:
                    if STATE_TERM in propertie:                        
                        state = self.normalizeAttributes(propertie, STATE_TERM)
                    elif TYPE_TERM in propertie:
                        type = self.normalizeAttributes(propertie, TYPE_TERM)
                    elif INSTANCE_ID_TERM in propertie:
                        instanceId = self.normalizeAttributes(propertie, INSTANCE_ID_TERM)
                
                id = properties[0]
                idRequestTable = id + ':' + instanceId
                request = {'id' : idRequestTable, 'requestId' : id, 'state' : state, 'type' : type, 'instanceId': instanceId}
                listRequests.append(Request(request))                
        
        return listRequests
    
    def normalizeAttributes(self, propertie, term):        
        return propertie.split(term)[1].replace('"', '').replace('=','')
    
class CreateView(forms.ModalFormView):
    form_class = CreateRequest
    template_name = 'fogbow/request/create.html'
    success_url = reverse_lazy('horizon:fogbow:index')
    
class DetailView(tabs.TabView):
    tab_group_class = project_tabs.RequestDetailTabs
    template_name = 'fogbow/request/detail.html'
