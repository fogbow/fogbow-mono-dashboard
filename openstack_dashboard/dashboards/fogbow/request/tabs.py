from django.utils.translation import ugettext_lazy as _ 
from horizon import tabs
import openstack_dashboard.dashboards.fogbow.instance.tabs as tabsInstanceDashboard
import openstack_dashboard.models as fogbow_request

COMPUTE_TERM = '/compute/'

class InstanceDetailTab(tabs.Tab):
    name = _("Instance Details")
    slug = "instance_details"
    template_name = ("fogbow/request/_detail_instance.html")

    def get_context_data(self, request):
        instanceId = self.tab_group.kwargs['instance_id'].split(':')[1]
                
        response = fogbow_request.doRequest('get', COMPUTE_TERM  + instanceId, None, request)
        
        return {'instance' : tabsInstanceDashboard.getInstancePerResponse(instanceId, response)}
                        
class RequestDetailTabs(tabs.TabGroup):
    slug = "requests_details"
    tabs = (InstanceDetailTab,)
