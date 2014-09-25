from horizon import views

import requests
from horizon import tables
from horizon import tabs

from django.core.urlresolvers import reverse_lazy  # noqa
from django.utils.translation import ugettext_lazy as _  # noqa

from horizon import forms
from horizon import exceptions
from django.conf import settings

from openstack_dashboard.dashboards.fogbow.request \
    import tabs as project_tabs
from openstack_dashboard.dashboards.fogbow.request \
    import tables as project_tables
from openstack_dashboard.dashboards.fogbow.request \
    import models as project_models    
from openstack_dashboard.dashboards.fogbow.request.forms import CreateRequest
from openstack_dashboard.dashboards.fogbow.request.models import Request
import openstack_dashboard.dashboards.fogbow.models as fogbow_request

class IndexView(tables.DataTableView):
    table_class = project_tables.RequestsTable
    template_name = 'fogbow/request/index.html'
    
    def has_more_data(self, table):
        return self._more

    def get_data(self):                
        response = fogbow_request.doRequest('get', '/fogbow_request', None)        
        if response.status_code < 200 and reponse.status_code > 204:
            print 'erro'                        
        
        responseStr = response.text    
        listRequests = self.returnRequestList(responseStr)
        
        self._more = False
        
        return listRequests

    def returnRequestList(self, responseStr):
        listRequests = []
        requestsId = responseStr.split('\n')
        for reqst in requestsId:
            reqst = reqst.split('/fogbow_request/')
            id = ''
            if len(reqst) > 1:
                reqst = reqst[1]
                reponseGetSpecificRequest = fogbow_request.doRequest('get', '/fogbow_request/' + reqst, None)
                reponseGetSpecificRequestStr = reponseGetSpecificRequest.text
                
                state, type, instanceId = '', '', ''
                properties = reponseGetSpecificRequestStr.split('\n')
                for p in properties:
                    if 'org.fogbowcloud.request.state=' in p:
                        p = p.split('org.fogbowcloud.request.state=')
                        p = p[1]
                        p = p.replace('"', '')
                        state = p
                    elif 'org.fogbowcloud.request.type=' in p:
                        p = p.split('org.fogbowcloud.request.type=')
                        p = p[1]
                        p = p.replace('"', '')
                        type = p
                    elif 'org.fogbowcloud.request.instance-id' in p:
                        p = p.split('org.fogbowcloud.request.instance-id')
                        p = p[1]
                        p = p.replace('"', '')
                        p = p.replace('=', '')
                        instanceId = p 
                        
                id = reqst + ':' + instanceId
                request = {'id' : id, 'requestId' : reqst, 'state' : state, 'type' : type, 'instanceId': instanceId}
                listRequests.append(Request(request))                
            
        return listRequests
    
class CreateView(forms.ModalFormView):
    form_class = CreateRequest
    template_name = 'fogbow/request/create.html'
    success_url = reverse_lazy('horizon:fogbow:index')
    
class DetailView(tabs.TabView):
    tab_group_class = project_tabs.RequestDetailTabs
    template_name = 'fogbow/request/detail.html'

