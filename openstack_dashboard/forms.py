import logging
import commands

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth import forms as django_auth_forms
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables
import openstack_dashboard.models as fogbow_models
from openstack_auth import exceptions

LOG = logging.getLogger(__name__)

FORM_TYPE_OPENNEBULA = 'opennebula'
FORM_TYPE_TOKEN = 'token'
FORM_TYPE_VOMS = 'voms'
LOCAL_TYPE_FORM = '_local'
FEDERATION_TYPE_FORM = '_federation'

class OpennebulaForm(django_auth_forms.AuthenticationForm):
    #endpoint = forms.CharField(label=_("Endpoint"),
    #widget=forms.TextInput(attrs={"autofocus": "autofocus"}))
    username = forms.CharField(label=_("User Name"),
        widget=forms.TextInput(attrs={"autofocus": "autofocus"}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput(render_value=False))
    federation = forms.CharField( label=_("Federation"), widget=forms.Textarea, 
                                  required=False )        
     
    def __init__(self, *args, **kwargs):
        super(OpennebulaForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['federation', 'username', 'password']
 
    @sensitive_variables()
    def clean(self):        
        opennebulaEndpoint = settings.FOGBOW_LOCAL_AUTH_ENDPOINT
        #opennebulaEndpoint = self.cleaned_data.get('endpoint')
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
          
        opennebulaCredentials = {'username':username, 'password':password} 
              
        self.user_cache = authenticate(request=self.request, formType=FORM_TYPE_OPENNEBULA,
                                credentials=opennebulaCredentials, endpoint=opennebulaEndpoint)
        
        if self.user_cache.errors == True:
            throwErrorMessage(self, _('Invalid Opennebula Credentials'))
        
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
            throwErrorMessage(self, _('Invalid Token'))
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
        
        # Implement ...
        vomsCredentials = {'voms':''}
        
        self.user_cache = authenticate(request=self.request, formType=FORM_TYPE_VOMS,
                                        credentials=vomsCredentials)
        
        if self.user_cache.errors == True:
            throwErrorMessage(self, _('Invalid Voms Proxy Init'))
        
        LOG.info('Successful login')
        
        return self.cleaned_data
    
class KeystoneFogbow(django_auth_forms.AuthenticationForm):
    
    region = forms.ChoiceField(label=_("Region"), required=False)
    #endpoint = forms.CharField(label=_("Endpoint"))
    username = forms.CharField(
        label=_("User Name"),
        widget=forms.TextInput(attrs={"autofocus": "autofocus",}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput(render_value=False))
    federation = forms.CharField( label=_("Federation"), widget=forms.Textarea, 
                                  required=False )
    
    tenantName = forms.CharField(label=_("Tenant Name"))

    def __init__(self, *args, **kwargs):
        super(KeystoneFogbow, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['federation', 'username', 'password', 'tenantName', 'region']
        #self.fields.keyOrder = ['endpoint', 'username', 'password', 'tenantName', 'federation', 'region']
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
        
        endpoint = settings.FOGBOW_LOCAL_AUTH_ENDPOINT
        #endpoint = self.cleaned_data.get('endpoint')
        newEndpoint = '%s/v2.0' % endpoint           
        
        federation = self.cleaned_data.get('federation')
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

#----------------------
# Mod
#----------------------



class AllForm(django_auth_forms.AuthenticationForm):        
    listFields = {}
    
    def __init__(self, *args, **kwargs):
        super(AllForm, self).__init__(*args, **kwargs)
                
        localAuthType = settings.FOGBOW_LOCAL_AUTH_TYPE
        federationAuthType = settings.FOGBOW_FEDERATION_AUTH_TYPE
                                 
        localFields = KeystoneFields(LOCAL_TYPE_FORM)                                                    
        if localAuthType == fogbow_models.IdentityPluginConstants.AUTH_KEYSTONE:
            localFields = KeystoneFields(LOCAL_TYPE_FORM)
        elif localAuthType == fogbow_models.IdentityPluginConstants.AUTH_VOMS:
            localFields = VOMSFields(LOCAL_TYPE_FORM)   
        elif localAuthType == fogbow_models.IdentityPluginConstants.AUTH_TOKEN:
            localFields = TokenFields(LOCAL_TYPE_FORM)
        elif localAuthType == fogbow_models.IdentityPluginConstants.AUTH_OPENNEBULA:
            localFields = OpennebulaFields(LOCAL_TYPE_FORM)               
        
        federationFields = KeystoneFields(FEDERATION_TYPE_FORM)
        if federationAuthType == fogbow_models.IdentityPluginConstants.AUTH_KEYSTONE:
            federationFields = KeystoneFields(FEDERATION_TYPE_FORM)
        elif federationAuthType == fogbow_models.IdentityPluginConstants.AUTH_VOMS:
            federationFields = VOMSFields(FEDERATION_TYPE_FORM)                    
        elif federationAuthType == fogbow_models.IdentityPluginConstants.AUTH_TOKEN:
            federationFields = TokenFields(FEDERATION_TYPE_FORM)
        elif federationAuthType == fogbow_models.IdentityPluginConstants.AUTH_OPENNEBULA:
            federationFields = OpennebulaFields(FEDERATION_TYPE_FORM)                                            
                     
        self.listFields = federationFields.getFields()
        self.listFields.update(localFields.getFields()) 
        
        listOr = [];
        listOr.extend(federationFields.getOrderFields())
        listOr.extend(localFields.getOrderFields())
        
        for key in self.listFields.keys():
            self.fields[key] = self.listFields[key]
          
        self.fields.keyOrder = listOr
        
    @sensitive_variables()
    def clean(self):
        localCrendentials = {}
        federationCrendentials = {}
         
        for key in self.listFields.keys():
            if LOCAL_TYPE_FORM in key:
                localCrendentials[key.replace(LOCAL_TYPE_FORM, '')] = self.cleaned_data.get(key)
            elif FEDERATION_TYPE_FORM in key:
                federationCrendentials[key.replace(FEDERATION_TYPE_FORM, '')] = self.cleaned_data.get(key)                                        
        
        localEndpoint = settings.FOGBOW_LOCAL_AUTH_ENDPOINT
        federationEndpoint = settings.FOGBOW_FEDERATION_AUTH_ENDPOINT    
        
        self.user_cache = authenticate(request=self.request,
                                        localCredentials=localCrendentials,
                                        federationCredentials=federationCrendentials,
                                        localEndpoint=localEndpoint,
                                        federationEndpoint=federationEndpoint)        
        
        if self.user_cache.errors == True:
            throwErrorMessage(self, _(self.user_cache.typeError))
        LOG.info('Successful login')
        
        return self.cleaned_data

class KeystoneFields():    
    type = None
    
    def __init__(self, type):
        self = self        
        #self.type = type
        self.username = 'username' + type
        self.password = 'password' + type
        self.tenantName = 'tenantName' + type
            
    def getFields(self):
        listFields = {}
        listFields[self.username] = forms.CharField(label=_("Username"), required=False)
        listFields[self.password] = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput(render_value=False), required=False)
        listFields[self.tenantName] = forms.CharField(label=_("Tenant Name"), required=False)
        return listFields
    
    def getOrderFields(self):
        return [self.username, self.password, self.tenantName]
    
class VOMSFields():    
    type = None
    
    def __init__(self, type):
        self = self
        #self.type = type
        self.voms = 'voms' + type  
            
    def getFields(self):
        listFields = {} 
        listFields[self.voms] = forms.CharField( label=_("Proxy Certificate"), 
                            widget=forms.Textarea, required=False)
        return listFields

    def getOrderFields(self):
        return [self.voms]    
    
class OpennebulaFields():    
    type = None
    
    def __init__(self, type):
        self = self
        #self.type = type  
        self.username = 'username' + type
        self.password = 'password' + type
            
    def getFields(self):
        listFields = {}
        listFields[self.username] = forms.CharField(label=_("User Name"),
            widget=forms.TextInput(attrs={"autofocus": "autofocus"}))
        listFields[self.password] = forms.CharField(label=_("Password"),
                                   widget=forms.PasswordInput(render_value=False),
                                   required=False)
        return listFields
    
    def getOrderFields(self):
        return [self.username, self.password]    
    
class TokenFields():    
    type = None
    
    def __init__(self, type):
        self = self
        #self.type = type
        self.token = 'token' + type  
            
    def getFields(self):
        listFields = {} 
        listFields[self.token] = forms.CharField( label=_("Token"), 
                            widget=forms.Textarea, required=False)
        return listFields
    
    def getOrderFields(self):
        return [self.token]