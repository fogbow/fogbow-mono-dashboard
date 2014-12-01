import netaddr
import requests
import openstack_dashboard.models as fogbow_models

from django.core.urlresolvers import reverse 
from django.core import validators
from django.utils.translation import ugettext_lazy as _  
from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon.utils import fields
from openstack_dashboard import api
from django.core.urlresolvers import reverse_lazy
from horizon import messages
from django import shortcuts

RESOURCE_TERM = fogbow_models.FogbowConstants.RESOURCE_TERM
REQUEST_TERM = fogbow_models.FogbowConstants.REQUEST_TERM
SCHEME_FLAVOR_TERM = 'http://schemas.fogbowcloud.org/template/resource#'
SCHEME_IMAGE_TERM = 'http://schemas.fogbowcloud.org/template/os#'

class CreateRequest(forms.SelfHandlingForm):
    TYPE_REQUEST = (('one-time', 'one-time'), ('persistent', 'persistent'))
    success_url = reverse_lazy("horizon:fogbow:request:index")
    
    count = forms.CharField(label=_('Count'),
                           error_messages={
                               'required': _('This field is required.'),
                               'invalid': _('The string may only contain'
                                            ' ASCII characters and numbers.')},
                           validators=[validators.validate_slug],
                           initial='1')
    flavor = forms.ChoiceField(label=_('Flavor'),
                               help_text=_('Flavor Fogbow'))    
    image = forms.ChoiceField(label=_('Image'),
                               help_text=_('Image Fogbow'))
    type = forms.ChoiceField(label=_('Type'),
                               help_text=_('Type Request'),
                               choices=TYPE_REQUEST)
    publicKey = forms.CharField(label=_('Public Key'),
                           error_messages={'invalid': _('The string may only contain'
                                            ' ASCII characters and numbers.')},
                           required=False, widget=forms.Textarea)        

    def __init__(self, request, *args, **kwargs):
        super(CreateRequest, self).__init__(request, *args, **kwargs)
        
        response = fogbow_models.doRequest('get', RESOURCE_TERM, None, request)
        
        flavorChoices,imageChoices = [],[]
        resources = response.text.split('\n')
        for resource in resources:
            if SCHEME_FLAVOR_TERM in resource and 'fogbow' in resource:
                resource = self.normalizeNameResource(resource)
                flavorChoices.append((resource,resource))
            elif SCHEME_IMAGE_TERM in resource and 'fogbow' in resource:
                resource = self.normalizeNameResource(resource)
                imageChoices.append((resource,resource))
                                        
        self.fields['flavor'].choices = flavorChoices
        self.fields['image'].choices = imageChoices

    def normalizeNameResource(self, resource):
        return resource.split(';')[0].replace('Category: ', '')

    def handle(self, request, data):
        try:
            publicKeyCategory, publicKeyAttribute = '',''             
            if data['publicKey'].strip() is not None and data['publicKey'].strip(): 
                publicKeyCategory = ',fogbow_public_key; scheme="http://schemas.fogbowcloud/credentials#"; class="mixin"'
                publicKeyAttribute = ',org.fogbowcloud.credentials.publickey.data=%s' % (data['publicKey'].strip())
                                    
            headers = {'Category' : 'fogbow_request; scheme="http://schemas.fogbowcloud.org/request#"; class="kind",%s; scheme="http://schemas.fogbowcloud.org/template/resource#"; class="mixin",%s; scheme="http://schemas.fogbowcloud.org/template/os#"; class="mixin"%s' 
                        % (data['flavor'].strip(), data['image'].strip(), publicKeyCategory),
                       'X-OCCI-Attribute' : 'org.fogbowcloud.request.instance-count=%s,org.fogbowcloud.request.type=%s%s' % (data['count'].strip(), data['type'].strip(), publicKeyAttribute)}

            response = fogbow_models.doRequest('post', REQUEST_TERM, headers, request)                                                
            
            if response != None and fogbow_models.isResponseOk(response.text) == True: 
                messages.success(request, _('Requests created'))
            
            return shortcuts.redirect(reverse("horizon:fogbow:request:index"))    
        except Exception:
            redirect = reverse("horizon:fogbow:request:index")
            exceptions.handle(request,
                              _('Unable to create Requests.'),
                              redirect=redirect)   
            
    def returnFormatResponse(self, responseStr):      
        responseFormated = ''
        requests = responseStr.split('\n')
        for request in requests:
            if fogbow_models.FogbowConstants.REQUEST_TERM in request:
                responseFormated += request.split(fogbow_models.FogbowConstants.REQUEST_TERM)[1]
                if requests[-1] != request:
                    responseFormated += ' , '
        return responseFormated
