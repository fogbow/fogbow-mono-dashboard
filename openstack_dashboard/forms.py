import logging
import commands

from django.conf import settings
from django.contrib.auth import authenticate, login  # noqa
from django.contrib.auth import forms as django_auth_forms
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables  # noqa

from openstack_auth import exceptions

LOG = logging.getLogger(__name__)

FORM_TYPE_OPENNEBULA = 'opennebula'
FORM_TYPE_TOKEN = 'token'
FORM_TYPE_VOMS = 'voms'

class OpennebulaForm(django_auth_forms.AuthenticationForm):
    endpoint = forms.CharField(label=_("Endpoint"),
    widget=forms.TextInput(attrs={"autofocus": "autofocus"}))
    username = forms.CharField(label=_("User Name"),
        widget=forms.TextInput(attrs={"autofocus": "autofocus"}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput(render_value=False))
     
    def __init__(self, *args, **kwargs):
        super(OpennebulaForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['endpoint', 'username', 'password']
 
    @sensitive_variables()
    def clean(self):                
        opennebulaEndpoint = self.cleaned_data.get('endpoint')
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
          
        opennebulaCredentials = {'username':username, 'password':password} 
              
        self.user_cache = authenticate(request=self.request, formType=FORM_TYPE_OPENNEBULA,
                                credentials=opennebulaCredentials, endpoint=opennebulaEndpoint)
        
        if self.user_cache.errors == True:
            throwErrorMessage(self, 'Invalid Opennebula Credentials')
        
        LOG.info('Successful login')
        
        return self.cleaned_data

class TokenForm(django_auth_forms.AuthenticationForm):

    token = forms.CharField( label=_("Token"), widget=forms.Textarea )
    
    def __init__(self, *args, **kwargs):
        super(TokenForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['token']
        
    @sensitive_variables()
    def clean(self):        
        token = self.cleaned_data.get('token')
        
        tokenCredentials = {'token':token}
        
        self.user_cache = authenticate(request=self.request, formType=FORM_TYPE_TOKEN,
                                        credentials=tokenCredentials)        
        
        if self.user_cache.errors == True:
            throwErrorMessage(self, 'Invalid Token')
        
        LOG.info('Successful login')
        
        return self.cleaned_data

class VomsForm(django_auth_forms.AuthenticationForm):

    serverName = forms.CharField(label=_('Server Name'))
    password = forms.CharField(label=_('Password'),
                               widget=forms.PasswordInput(render_value=False))
    pathUserCred = forms.FileField(label=_('User Credentials'), required=False)
    pathUserKey = forms.FileField(label=_('User Key'), required=False)
                               
    
    def __init__(self, *args, **kwargs):
        super(VomsForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['serverName', 'password', 'pathUserCred', 'pathUserKey']
                
    @sensitive_variables()
    def clean(self):
        serverName = self.cleaned_data.get('serverName')
        password = self.cleaned_data.get('password')
        pathUserCred = self.cleaned_data.get('pathUserCred')
        pathUserKey = self.cleaned_data.get('pathUserKey')
        
        print password
        print pathUserCred
        print pathUserKey
        
        # Implement ...
        vomsCredentials = {'voms':''}
        
        self.user_cache = authenticate(request=self.request, formType=FORM_TYPE_VOMS,
                                        credentials=vomsCredentials)
        
        if self.user_cache.errors == True:
            throwErrorMessage(self, 'Invalid Voms Proxy Init')
        
        LOG.info('Successful login')
        
        return self.cleaned_data
    
class KeystoneFogbow(django_auth_forms.AuthenticationForm):
    
    region = forms.ChoiceField(label=_("Region"), required=False)
    endpoint = forms.CharField(label=_("Endpoint"))
    username = forms.CharField(
        label=_("User Name"),
        widget=forms.TextInput(attrs={"autofocus": "autofocus"}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput(render_value=False))
    tenantName = forms.CharField(label=_("Tenant Name"))

    def __init__(self, *args, **kwargs):
        super(KeystoneFogbow, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['endpoint', 'username', 'password', 'tenantName', 'region']
        if getattr(settings,
                   'OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT',
                   False):
            self.fields['domain'] = forms.CharField(label=_("Domain"),
                                                    required=True)
            self.fields.keyOrder = ['domain', 'username', 'password', 'region']
        self.fields['region'].choices = self.get_region_choices()
        if len(self.fields['region'].choices) == 1:
            self.fields['region'].initial = self.fields['region'].choices[0][0]
            self.fields['region'].widget = forms.widgets.HiddenInput()

    @staticmethod
    def get_region_choices():
        default_region = (settings.OPENSTACK_KEYSTONE_URL, "Default Region")
        return getattr(settings, 'AVAILABLE_REGIONS', [default_region])

    @sensitive_variables()
    def clean(self):
        default_domain = getattr(settings,
                                 'OPENSTACK_KEYSTONE_DEFAULT_DOMAIN',
                                 'Default')
        
        endpoint = self.cleaned_data.get('endpoint')
        newEndpoint = '%s/v2.0' % endpoint           
        
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        tenantName = self.cleaned_data.get('tenantName')
        region = self.cleaned_data.get('region')
        domain = self.cleaned_data.get('domain', default_domain)

        if not (username and password and endpoint):
            return self.cleaned_data

        try:
            self.user_cache = authenticate(request=self.request,
                                           username=username,
                                           password=password,
                                           user_domain_name=domain,
                                           auth_url=newEndpoint,
                                           tenantName = tenantName)            
            
            msg = 'Login successful for user "%(username)s".' % {'username': username}
            LOG.info(msg)
        except exceptions.KeystoneAuthException as exc:
            msg = 'Login failed for user "%(username)s".' % {'username': username}
            LOG.warning(msg)
            self.request.session.flush()
            raise forms.ValidationError(exc)
        if hasattr(self, 'check_for_test_cookie'):
            self.check_for_test_cookie()
        return self.cleaned_data
    
def throwErrorMessage(self, message):
    self.error_messages.update({'invalid_login_fogbow':_(message)})
    LOG.warning('Invalid Login.')
    raise forms.ValidationError(self.error_messages['invalid_login_fogbow'])
