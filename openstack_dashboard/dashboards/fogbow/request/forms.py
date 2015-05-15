import netaddr
import requests
import openstack_dashboard.models as fogbow_models

from django.core.validators import RegexValidator
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
    
    count = forms.CharField(label=_('Number of requests'),
                           error_messages={
                               'required': _('This field is required.'),
                               'invalid': _('The string may only contain'
                                            ' ASCII characters and numbers.')},
                           validators=[validators.validate_slug],
                           initial='1')
    
    cpu = forms.CharField(label=_('Minimal number of vCPUs'), initial=1,
                          widget=forms.TextInput(),
                          required=False)
    mem = forms.CharField(label=_('Minimal amount of RAM in MB'), initial=1024,
                          widget=forms.TextInput(),
                          required=False)
    advanced_requirements = forms.CharField(label=_('Advanced requirements'),
                           error_messages={'invalid': _('The string may only contain'
                                            ' ASCII characters and numbers.')},
                           required=False, widget=forms.Textarea)
    image = forms.CharField(label=_('Image'),
                           error_messages={
                               'required': _('This field is required.'),
                               'invalid': _('The string may only contain'
                                            ' ASCII characters and numbers.')})
    type = forms.ChoiceField(label=_('Type'),
                               help_text=_('Type Request'),
                               choices=TYPE_REQUEST)
    
    data_user = forms.FileField(label=_('Extra user data file'), required=False)
    
    data_user_type = forms.ChoiceField(label=_('Extra user data file type'),
                           help_text=_('Data user type'),
                           required=False)
    
    publicKey = forms.CharField(label=_('Public Key'),
                           error_messages={'invalid': _('The string may only contain'
                                            ' ASCII characters and numbers.')},
                           required=False, widget=forms.Textarea)
    
    data_user_file = forms.CharField(label=_('hidden'), required=False, widget=forms.Textarea)            

    def __init__(self, request, *args, **kwargs):
        super(CreateRequest, self).__init__(request, *args, **kwargs)
        
        response = fogbow_models.doRequest('get', RESOURCE_TERM, None, request)

        dataUserTypeChoices = []
        dataUserTypeChoices.append(('text/x-shellscript', 'text/x-shellscript'))
        dataUserTypeChoices.append(('text/x-include-once-url', 'text/x-include-once-url'))
        dataUserTypeChoices.append(('text/x-include-url', 'text/x-include-url'))
        dataUserTypeChoices.append(('text/cloud-config-archive', 'text/cloud-config-archive'))
        dataUserTypeChoices.append(('text/upstart-job', 'text/upstart-job'))
        dataUserTypeChoices.append(('text/cloud-config', 'text/cloud-config'))        
        dataUserTypeChoices.append(('text/cloud-boothook', 'text/cloud-boothook'))
        self.fields['data_user_type'].choices = dataUserTypeChoices

    def normalizeNameResource(self, resource):
        return resource.split(';')[0].replace('Category: ', '')

    def normalizeValueHeader(self, value):
        try:
            return value.replace('\n','').replace('\r','')
        except Exception:
            return ''

    def normalizeUserData(self, value):
        try:
            return value.replace('\n', '[[\\n]]')
        except Exception:
            return ''

    def handle(self, request, data):
        try:
            publicKeyCategory, publicKeyAttribute = '',''             
            if data['publicKey'].strip() is not None and data['publicKey'].strip(): 
                publicKeyCategory = ',fogbow_public_key; scheme="http://schemas.fogbowcloud/credentials#"; class="mixin"'                
                publicKeyAttribute = ',org.fogbowcloud.credentials.publickey.data=%s' % (data['publicKey'].strip())
            
            advancedRequirements = ''
            if data['advanced_requirements'] != '':
                advancedRequirements = ',org.fogbowcloud.request.requirements=%s' % (data['advanced_requirements'])
                advancedRequirements = self.normalizeValueHeader(advancedRequirements)
            else:
                advancedRequirements = ''
            
            userDataAttribute = ''
            if data['data_user_file'] != None or data['data_user_file'] != '':
                print data['data_user_file']
                userDataContent = ',org.fogbowcloud.request.extra-user-data="%s"' % (data['data_user_file'])
                dataUserType = ''
                if data['data_user_type'] != 'None':
                    userDataAttribute = ',org.fogbowcloud.request.extra-user-data-content-type="%s"%s' % (data['data_user_type'], userDataContent)
                    userDataAttribute = self.normalizeUserData(userDataAttribute)                      
                
            headers = {'Category' : 'fogbow_request; scheme="http://schemas.fogbowcloud.org/request#"; class="kind"%s,%s; scheme="http://schemas.fogbowcloud.org/template/os#"; class="mixin"%s' 
                        % ('', data['image'].strip(), publicKeyCategory),
                       'X-OCCI-Attribute' : 'org.fogbowcloud.request.instance-count=%s,org.fogbowcloud.request.type=%s%s%s%s' % (data['count'].strip(), data['type'].strip(), publicKeyAttribute, advancedRequirements, userDataAttribute)}            

         #   response = fogbow_models.doRequest('post', REQUEST_TERM, headers, request)
            
            if response != None and fogbow_models.isResponseOk(response.text) == True: 
                messages.success(request, _('Requests created'))
            
            return shortcuts.redirect(reverse("horizon:fogbow:request:index"))    
        except Exception:
            redirect = reverse("horizon:fogbow:request:index")
            exceptions.handle(request,
                              _('Unable to create requests.'),
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
