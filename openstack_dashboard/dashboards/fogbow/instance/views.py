from horizon import views

import requests

from django.core.urlresolvers import reverse_lazy  # noqa
from django.utils.translation import ugettext_lazy as _  # noqa

from horizon import exceptions
from horizon import tables
from horizon import tabs
from django.conf import settings

from openstack_dashboard.dashboards.fogbow.instance \
    import tabs as project_tabs
from openstack_dashboard.dashboards.fogbow.instance \
    import tables as project_tables
from openstack_dashboard.dashboards.fogbow.instance \
    import models as project_models    
import openstack_dashboard.models as fogbow_request

# LOG = logging.getLogger(__name__)

COMPUTE_TERM = '/compute/'

class IndexView(tables.DataTableView):
    table_class = project_tables.InstancesTable
    template_name = 'fogbow/instance/index.html'

    def has_more_data(self, table):
        return self._more

    def get_data(self):
        response = fogbow_request.doRequest('get', COMPUTE_TERM, None,
                                                     self.request.session.get('token','').id)   
        responseStr = response.text
        instances = []        
        try:
            properties =  memberProperties = responseStr.split('\n')
            for propertie in properties:
                idInstance = self.normalizeAttribute(propertie)
                instance = {'id': idInstance, 'instanceId': idInstance}
                instances.append(project_models.Instance(instance))            
        except Exception:
            print ''
        
        self._more = False
        
        return instances  
    
    def normalizeAttribute(self, propertie):
        return propertie.replace('X-OCCI-Location: ', '')
    
class DetailView2(tabs.TabView):
    tab_group_class = project_tabs.InstanceDetailTabs2
    template_name = 'fogbow/instance/detail.html'     
        