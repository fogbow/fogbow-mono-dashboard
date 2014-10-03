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
        requestsFullfield, requestsOpen, requestsClosed = 0, 0, 0
        for request in requests:
            if 'FULFILLED' in request:
                requestsFullfield += 1
            elif 'OPEN' in request:
                requestsOpen += 1
            elif 'CLOSED' in request:
                requestsClosed += 1

        totalRequest = len(requests)
        context['requestsFullfield'] = requestsFullfield
        context['requestsFullfieldPercent'] = (requestsFullfield * 100) / totalRequest
        context['requestsOpen'] = requestsOpen
        context['requestsOpenPercent'] = (requestsOpen * 100) / totalRequest
        context['requestsClosed'] = requestsClosed
        context['requestsClosedPercent'] = (requestsClosed * 100) / totalRequest
        context['requestsTotal'] = totalRequest
        return context