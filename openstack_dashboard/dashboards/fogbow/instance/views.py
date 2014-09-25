from horizon import views

import requests

from django.core.urlresolvers import reverse_lazy  # noqa
from django.utils.translation import ugettext_lazy as _  # noqa

from horizon import exceptions
from horizon import tables
from django.conf import settings

from openstack_dashboard.dashboards.fogbow.instance \
    import tables as project_tables
from openstack_dashboard.dashboards.fogbow.instance \
    import models as project_models    

# LOG = logging.getLogger(__name__)

class IndexView(tables.DataTableView):
    table_class = project_tables.InstancesTable
    template_name = 'fogbow/instance/index.html'

    def has_more_data(self, table):
        return self._more

    def get_data(self):
        instances = []    

        headers = {'content-type': 'text/occi', 'X-Auth-Token' : settings.MY_TOKEN}
         
        r = requests.get(settings.MY_ENDPOINT + '/compute/', headers=headers)
        data = r.text                
        
        try:
            instancesIds =  memberProperties = data.split('\n')
            for instance in instancesIds:
                instance = instance.replace('X-OCCI-Location: ', '')
                instance1 = {'id': instance, 'instanceId': instance}
                instances.append(project_models.Instance(instance1))            
        except Exception:
            x = "" 
        
        self._more = False
        
        return instances  
    