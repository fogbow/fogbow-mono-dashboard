import netaddr
import requests
import openstack_dashboard.models as fogbow_models
import base64

from django.core.validators import RegexValidator
from django.core.urlresolvers import reverse 
from django.core import validators
from django.utils.translation import ugettext_lazy as _  
from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon.utils import fields
from django.core.urlresolvers import reverse_lazy
from horizon import messages
from django import shortcuts
from openstack_dashboard.dashboards.fogbow.members.views import IndexView as member_views

RESOURCE_TERM = fogbow_models.FogbowConstants.RESOURCE_TERM
MEMBER_TERM = fogbow_models.FogbowConstants.MEMBER_TERM
REQUEST_TERM = fogbow_models.FogbowConstants.REQUEST_TERM
STORAGE_TERM = fogbow_models.FogbowConstants.STORAGE_TERM
NETWORK_TERM = fogbow_models.FogbowConstants.NETWORK_TERM
ORDER_TERM_CATEGORY = 'order'
REQUEST_TERM_CATEGORY = ORDER_TERM_CATEGORY
REQUEST_SCHEME = fogbow_models.FogbowConstants.REQUEST_SCHEME
ORDER_SCHEME = fogbow_models.FogbowConstants.ORDER_SCHEME
SCHEME_FLAVOR_TERM = 'http://schemas.fogbowcloud.org/template/resource#'
SCHEME_IMAGE_TERM = 'http://schemas.fogbowcloud.org/template/os#'
FOGBOW_RESOURCE_KIND_TERM = fogbow_models.FogbowConstants.FOGBOW_RESOURCE_KIND_TERM
SIZE_OCCI = fogbow_models.FogbowConstants.SIZE_OCCI
STORAGE_SCHEME = fogbow_models.FogbowConstants.STORAGE_SCHEME

class CreateRequest(forms.SelfHandlingForm):
    success_url = reverse_lazy("horizon:fogbow:request:index")
    
    count = forms.CharField(label=_('Number of orders'),
                           error_messages={
                               'required': _('This field is required.'),
                               'invalid': _('The string may only contain'
                                            ' ASCII characters and numbers.')},
                           validators=[validators.validate_slug],
                           initial='1')
    
    cird = forms.CharField(label=_('CIDR'), initial='192.168.0.0/24',
                          widget=forms.TextInput(),
                          required=False)

    gateway = forms.CharField(label=_('Gateway'), initial='',
                          widget=forms.TextInput(),
                          required=False)
    
    members = forms.ChoiceField(label=_('Members'), help_text=_('Members'), required=False)
    
    def __init__(self, request, *args, **kwargs):
        super(CreateRequest, self).__init__(request, *args, **kwargs)
        
        response = fogbow_models.doRequest('get', RESOURCE_TERM, None, request)
        
        membersChoices = []
        membersChoices.append(('', 'Try first local, then any'))
        try:
            membersResponseStr = fogbow_models.doRequest('get', MEMBER_TERM, None, request).text
            members = member_views().getMembersList(fogbow_models.doRequest('get', MEMBER_TERM, None, request).text)
            for m in members:
                membersChoices.append((m.get('idMember'), m.get('idMember')))
        except Exception as error: 
            pass        

        self.fields['members'].choices = membersChoices
        

    def normalizeNameResource(self, resource):
        return resource.split(';')[0].replace('Category: ', '')

    def normalizeValueHeader(self, value):
        try:
            return value.replace('\n','').replace('\r','')
        except Exception:
            return ''

    def normalizeUserData(self, value):
        try:
            return base64.b64encode(value.replace('\n', '[[\\n]]').replace('\r', ''))
        except Exception:
            return ''

    def handle(self, request, data):
        try:
            if self.checkAllAttributes(data, request) == False:
                return None
            
            advancedRequirements = ''
            if data['advanced_requirements'] != '':
                advancedRequirements = ',org.fogbowcloud.order.requirements=%s' % (data['advanced_requirements'])
                advancedRequirements = self.normalizeValueHeader(advancedRequirements)
            else:
                advancedRequirements = ''
            
            headers = {}
            attrCIRD, attrGateway, attrAllocation = '', '', ''
            cird = data['cird']
            gateway = data['gateway']
            allocation = data['allocation']
            if cird is not None and cird is not '':
                attrGateway = '%s=%s,' % ('occi.network.address', cird)
            if gateway is not None and gateway is not '':
                attrCIRD = '%s=%s,' % ('occi.network.gateway', gateway)
            if allocation is not None and allocation is not '':
                attrAllocation = '%s=%s' % ('occi.network.allocation', allocation)                            
            
            headers = {'Category' : '%s; %s; class="kind"' % (REQUEST_TERM_CATEGORY, REQUEST_SCHEME), 'X-OCCI-Attribute' : '%s%s%s' % (attrCIRD, attrGateway, attrAllocation)}

            addHeader = headers.get('X-OCCI-Attribute')
            headers.update({'X-OCCI-Attribute': addHeader + ', %s=%s' % (FOGBOW_RESOURCE_KIND_TERM, 'network')})
            if advancedRequirements != '':
                addHeader = headers.get('X-OCCI-Attribute')
                headers.update({'X-OCCI-Attribute': addHeader + '%s' % (advancedRequirements)})                                

            response = fogbow_models.doRequest('post', REQUEST_TERM, headers, request)
            
            if response != None and fogbow_models.isResponseOk(response.text) == True: 
                messages.success(request, _('Orders created'))
            
            return shortcuts.redirect(reverse("horizon:fogbow:request:index"))    
        except Exception:
            redirect = reverse("horizon:fogbow:request:index")
            exceptions.handle(request,
                              _('Unable to create orders.'),
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
    
    def checkAllAttributes(self, data, request):
        value = None
        if self.existsBreakline(str(data['publicKey']).strip())== True:
            value = 'public key'
        if self.existsBreakline(str(data['count']).strip())== True:
            value = 'count'
        if self.existsBreakline(str(data['sizeStorage']).strip())== True:
            value = 'size storage'
        
        if value is not None:
            messages.error(request, _('Wrong sintax. There is a breakline in the %s field.' % (value)))
            return False
        return True   
                
    def existsBreakline(self, attribute):
        auxList = {'att': attribute}
        if '\n' in auxList['att'] or '\r\n' in auxList['att']:
            return True
        return False