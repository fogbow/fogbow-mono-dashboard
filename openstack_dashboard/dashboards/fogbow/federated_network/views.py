from horizon import views
from django.utils.translation import ugettext_lazy as _  # noqa
from horizon import tables
from horizon import tabs

from openstack_dashboard.dashboards.fogbow.federated_network \
    import tabs as project_tabs
from openstack_dashboard.dashboards.fogbow.federated_network \
    import tables as project_tables
from openstack_dashboard.dashboards.fogbow.federated_network \
    import models as project_models    
import openstack_dashboard.models as fogbow_models

THERE_ARE_NOT_INSTANCE = 'There are not instances'
X_OCCI_LOCATION = 'X-OCCI-Location: '
NETWORK_TERM = fogbow_models.FogbowConstants.NETWORK_TERM

class IndexView(tables.DataTableView):
    table_class = project_tables.InstancesTable
    template_name = 'fogbow/federated_network/index.html'

    def get_data(self):
        instances = []   
        
        return instances
    
    def normalizeAttribute(self, propertie):
        return propertie.replace(X_OCCI_LOCATION, '')

    def getInstances(self, responseStr):
        responseStr = "id:1; allowed:150.165.85.32/28; providers:A,B\n" \
                       "id:2; allowed:178.52.32.0/27; providers:C"
        instances = []
        print responseStr
        try:            
            if fogbow_models.isResponseOk(responseStr):                         
                fednets =  responseStr.split('\n')
                for fednet in fednets:
                    id, allowed, providers = fednet.split(';')
                    id = id.split(':')[1]
                    allowed = allowed.split(':')[1]
                    providers = providers.split(':')[1]
                    instance = {'id': id, 'allowed': allowed, 'providers': providers}
                    if areThereInstance(responseStr):
                        instances.append(project_models.Instance(instance))                                
        except Exception:
            instances = []
            
        return instances
        
def areThereInstance(responseStr):
    if THERE_ARE_NOT_INSTANCE in responseStr:
        return False
    return True 

class DetailViewInstance(tabs.TabView):
    tab_group_class = project_tabs.InstanceDetailTabGroupInstancePanel
    template_name = 'fogbow/federated_network/detail.html'     
        