import openstack_dashboard.models as fogbow_models
from horizon import views
from django.utils.translation import ugettext_lazy as _

REQUEST_TERM = fogbow_models.FogbowConstants.REQUEST_TERM_WITH_VERBOSE
FULFILLED_STATUS_REQUEST = 'FULFILLED'
OPEN_STATUS_REQUEST = 'OPEN'
CLOSED_STATUS_REQUEST = 'CLOSED'
DELETED_STATUS_REQUEST = 'DELETED'
FAILED_STATUS_REQUEST = 'FAILED'
TOTAL = 'TOTAL'

class IndexView(views.APIView):
    template_name = 'fogbow/overview/index.html'

    def get_data(self, request, context, *args, **kwargs):                        
        response = fogbow_models.doRequest('get', REQUEST_TERM, None, request)
                                          
        return self.getContextOverview(response.text, context)
    
    def getContextOverview(self, responseStr, context):    
        mapCountRequests = getMapCountRequests(responseStr)    
        context['requestsFullfield'] = mapCountRequests[FULFILLED_STATUS_REQUEST]
        context['requestsOpen'] = mapCountRequests[OPEN_STATUS_REQUEST]
        context['requestsClosed'] = mapCountRequests[CLOSED_STATUS_REQUEST]
        context['requestsDeleted'] = mapCountRequests[DELETED_STATUS_REQUEST]
        context['requestsFailed'] = mapCountRequests[FAILED_STATUS_REQUEST]
        context['requestsTotal'] = mapCountRequests[TOTAL]        
        context['requestsOpenPercent'] = fogbow_models.calculatePercent(mapCountRequests[OPEN_STATUS_REQUEST],
                                                           mapCountRequests[TOTAL])
        context['requestsClosedPercent'] = fogbow_models.calculatePercent(mapCountRequests[CLOSED_STATUS_REQUEST],
                                                           mapCountRequests[TOTAL])
        context['requestsFailedPercent'] = fogbow_models.calculatePercent(mapCountRequests[FAILED_STATUS_REQUEST],
                                                           mapCountRequests[TOTAL])          
        context['requestsDeletedPercent'] = fogbow_models.calculatePercent(mapCountRequests[DELETED_STATUS_REQUEST], 
                                                           mapCountRequests[TOTAL])
        context['requestsFullfieldPercent'] = fogbow_models.calculatePercent(mapCountRequests[FULFILLED_STATUS_REQUEST],
                                                           mapCountRequests[TOTAL])             
        
        context['text_description_fogbow'] = _('Federation, opportunism and greenness in private infrastructure-as-a-service clouds through the bartering of wares')
        
        return context
       
def getMapCountRequests(responseStr):
    requests = responseStr.split('\n')
    requestsFullfield, requestsOpen, requestsClosed, requestsDeleted ,requestsFailed = 0, 0, 0, 0, 0
    for request in requests:
        if FULFILLED_STATUS_REQUEST in request:
            requestsFullfield += 1
        elif OPEN_STATUS_REQUEST in request:
            requestsOpen += 1
        elif CLOSED_STATUS_REQUEST in request:
            requestsClosed += 1
        elif DELETED_STATUS_REQUEST in request:
            requestsDeleted += 1
        elif FAILED_STATUS_REQUEST in request:
            requestsFailed += 1
            
    totalRequest = requestsFullfield + requestsOpen + requestsClosed + requestsDeleted + requestsFailed
    
    return {FULFILLED_STATUS_REQUEST: requestsFullfield, OPEN_STATUS_REQUEST: requestsOpen,
            CLOSED_STATUS_REQUEST: requestsClosed, DELETED_STATUS_REQUEST: requestsDeleted,
            FAILED_STATUS_REQUEST: requestsFailed, TOTAL: totalRequest}
    