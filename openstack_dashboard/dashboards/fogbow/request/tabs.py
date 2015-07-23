from django.utils.translation import ugettext_lazy as _ 
from horizon import tabs
import openstack_dashboard.dashboards.fogbow.instance.tabs as tabsInstanceDashboard
import openstack_dashboard.models as fogbow_models
import base64

COMPUTE_TERM = fogbow_models.FogbowConstants.COMPUTE_TERM
REQUEST_TERM = fogbow_models.FogbowConstants.REQUEST_TERM

IMAGE_SCHEME = fogbow_models.FogbowConstants.IMAGE_SCHEME     
FOGBOW_SHH_PUBLIC_KEY_TERM = fogbow_models.FogbowConstants.FOGBOW_SHH_PUBLIC_KEY_REQUEST_TERM 
FOGBOW_REQUIREMENTS_TERM = fogbow_models.FogbowConstants.FOGBOW_REQUIREMENTS_TERM
FOGBOW_USERDATA_TERM = fogbow_models.FogbowConstants.FOGBOW_USERDATA_TERM
FOGBOW_USERDATA_CONTENT_TYPE_TERM = fogbow_models.FogbowConstants.FOGBOW_USERDATA_CONTENT_TYPE_TERM
FOGBOW_VALID_FROM_TERM = fogbow_models.FogbowConstants.FOGBOW_VALID_FROM_TERM
FOGBOW_VALID_UNTIL_TERM = fogbow_models.FogbowConstants.FOGBOW_VALID_UNTIL_TERM    
FOGBOW_STATE_TERM = fogbow_models.FogbowConstants.FOGBOW_STATE_TERM
FOGBOW_TYPE_TERM = fogbow_models.FogbowConstants.FOGBOW_TYPE_TERM
FOGBOW_INSTANCE_ID_TERM = fogbow_models.FogbowConstants.FOGBOW_INSTANCE_ID_TERM
FOGBOW_COUNT_TERM = fogbow_models.FogbowConstants.FOGBOW_COUNT_TERM


class InstanceDetailTab(tabs.Tab):
    name = _("Instance Details")
    slug = "instance_details"
    template_name = ("fogbow/instance/_detail_instance.html")

    def get_context_data(self, request):
        instanceId = self.tab_group.kwargs['instance_id'].split(':')[1]
                
        response = fogbow_models.doRequest('get', COMPUTE_TERM  + instanceId, None, request)
        
        return {'instance' : tabsInstanceDashboard.getInstancePerResponse(instanceId, response)}
    
class RequestDetailTab(tabs.Tab):
    name = _("Request Details")
    slug = "request_details"
    template_name = ("fogbow/request/_detail_request.html")

    def get_context_data(self, request):
        requestId = self.tab_group.kwargs['instance_id'].split(':')[0]
                
        response = fogbow_models.doRequest('get', REQUEST_TERM  + requestId, None, request)
        
        return {'request' : self.getRequestPerResponse(requestId, response)}
    
    def normalizeUserdate(self, extraUserdata):
        if 'Not defined' in extraUserdata:
            return extraUserdata
        try:
            extraUserdata = base64.b64decode(extraUserdata + '==')
            return  extraUserdata.replace('[[\\n]]', '\n').strip()
        except Exception, e:            
            print str(e)   
    
    def getRequestPerResponse(self, requestId, response):
        if requestId == 'null':
            requestId = '-'
        
        print response.text
        requestDetails = response.text.split('\n')
        
        requirements, type, state, validFrom, validUntil, image, ssh, extraUserdata, extraUserdataContentType, instanceId, count  = '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'
        for detail in requestDetails:
            if FOGBOW_REQUIREMENTS_TERM in detail:
                requirements = tabsInstanceDashboard.normalizeAttributes(detail, FOGBOW_REQUIREMENTS_TERM)
            elif FOGBOW_SHH_PUBLIC_KEY_TERM in detail:
                ssh = tabsInstanceDashboard.normalizeAttributes(detail, FOGBOW_SHH_PUBLIC_KEY_TERM)
            elif FOGBOW_USERDATA_TERM + '=' in detail:
                extraUserdata = tabsInstanceDashboard.normalizeAttributes(detail, FOGBOW_USERDATA_TERM)                                
                extraUserdata = self.normalizeUserdate(extraUserdata)
            elif FOGBOW_USERDATA_CONTENT_TYPE_TERM in detail:
                extraUserdataContentType = tabsInstanceDashboard.normalizeAttributes(detail, FOGBOW_USERDATA_CONTENT_TYPE_TERM)                                
            elif FOGBOW_TYPE_TERM in detail:
                type = tabsInstanceDashboard.normalizeAttributes(detail, FOGBOW_TYPE_TERM)
            elif FOGBOW_COUNT_TERM in detail:
                count = tabsInstanceDashboard.normalizeAttributes(detail, FOGBOW_COUNT_TERM)                               
            elif FOGBOW_STATE_TERM in detail:
                state = tabsInstanceDashboard.normalizeAttributes(detail, FOGBOW_STATE_TERM)
            elif FOGBOW_VALID_FROM_TERM in detail:
                validFrom = tabsInstanceDashboard.normalizeAttributes(detail, FOGBOW_VALID_FROM_TERM)
            elif IMAGE_SCHEME in detail:
                image = tabsInstanceDashboard.getFeatureInCategoryPerScheme('title', detail)
            elif FOGBOW_VALID_UNTIL_TERM in detail:
                validUntil = tabsInstanceDashboard.normalizeAttributes(detail, FOGBOW_VALID_UNTIL_TERM)
            elif FOGBOW_INSTANCE_ID_TERM in detail:
                instanceId = tabsInstanceDashboard.normalizeAttributes(detail, FOGBOW_INSTANCE_ID_TERM)
                if 'null' in instanceId:
                    instanceId = 'Not defined'
            elif 'org.fogbowcloud.request.user-data' in detail:
                extra = tabsInstanceDashboard.normalizeAttributes(detail, 'org.fogbowcloud.request.user-data')                    
                
        return {'requestId': requestId , 'requirements': requirements, 'type':type,
                 'state' : state, 'validFrom' : validFrom, 'validUntil' : validUntil,
                'image' : image, 'ssh': ssh, 'extraUserdata': extraUserdata, 
                'extraUserdataContentType': extraUserdataContentType, 'instanceId': instanceId,
                'count': count}
                        
class InstanceDetailTabs(tabs.TabGroup):
    slug = "instances_details"
    tabs = (InstanceDetailTab,)
    
class RequestDetailTabs(tabs.TabGroup):
    slug = "requests_details"
    tabs = (RequestDetailTab,)
