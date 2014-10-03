from horizon import views

import openstack_dashboard.models as fogbow_request
REQUEST_TERM = '/fogbow_request?verbose=true'

class IndexView(views.APIView):
    template_name = 'fogbow/overview/index.html'

    def get_data(self, request, context, *args, **kwargs):        
        response = fogbow_request.doRequest('get', REQUEST_TERM, None,
                                             self.request.session.get('token','').id)
        
                        
                  
        return context
    
    def setValues(self, responseStr):
        print
