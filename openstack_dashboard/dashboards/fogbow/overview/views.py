from horizon import views

import openstack_dashboard.models as fogbow_request

REQUEST_TERM = '/fogbow_request?verbose=true'

class IndexView(views.APIView):
    template_name = 'fogbow/overview/index.html'

    def get_data(self, request, context, *args, **kwargs):        
        response = fogbow_request.doRequest('get', REQUEST_TERM, None,
                                             self.request.session.get('token','').id)                                
                                          
        return self.setValues(response.text, context)
    
    def setValues(self, responseStr, context):
        requests = responseStr.split('\n')
        requestsFullfield, requestsOpen, requestsClosed, requestsDeleted ,requestsFailed = 0, 0, 0, 0, 0
        for request in requests:
            if 'FULFILLED' in request:
                requestsFullfield += 1
            elif 'OPEN' in request:
                requestsOpen += 1
            elif 'CLOSED' in request:
                requestsClosed += 1
            elif 'DELETED' in request:
                requestsDeleted += 1
            elif 'FAILED' in request:
                requestsFailed += 1

        totalRequest = requestsFullfield + requestsOpen + requestsClosed + requestsDeleted + requestsFailed 
        context['requestsFullfield'] = requestsFullfield
        context['requestsOpen'] = requestsOpen
        context['requestsClosed'] = requestsClosed
        context['requestsDeleted'] = requestsDeleted
        context['requestsFailed'] = requestsFailed
        if totalRequest is not 0:
            context['requestsOpenPercent'] = (requestsOpen * 100) / totalRequest
            context['requestsClosedPercent'] = (requestsClosed * 100) / totalRequest
            context['requestsFailedPercent'] = (requestsFailed * 100) / totalRequest            
            context['requestsDeletedPercent'] = (requestsDeleted * 100) / totalRequest    
            context['requestsFullfieldPercent'] = (requestsFullfield * 100) / totalRequest
        else:
            context['requestsOpenPercent'] = 0
            context['requestsClosedPercent'] = 0
            context['requestsFailedPercent'] = 0            
            context['requestsDeletedPercent'] = 0    
            context['requestsFullfieldPercent'] = 0        
        context['requestsTotal'] = totalRequest        
        
        return context
       