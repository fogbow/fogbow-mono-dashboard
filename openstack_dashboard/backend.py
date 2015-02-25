import logging
import commands
import uuid

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from keystoneclient import exceptions as keystone_exceptions
from openstack_auth import exceptions
from openstack_auth import user as auth_user
from openstack_auth import utils
from openstack_dashboard.models import User
from openstack_dashboard.models import Token
import openstack_dashboard.forms as form_fogbow
import openstack_dashboard.models as fogbow_models


LOG = logging.getLogger(__name__)

FOGBOW_CLI_JAVA_COMMAND = 'java -cp fogbow-cli-0.0.1-SNAPSHOT-jar-with-dependencies.jar org.fogbowcloud.cli.Main $@'

class FogbowBackend(object):
  
    _cached_tokens = {}
    DEFAULT_FOGBOW_NAME = 'Fogbow User'
  
    def check_auth_expiry(self, user, margin=None):
        return True
  
    def get_user(self, user_id):     
        federationToken = self._cached_tokens[self.request.session['token']]
        localToken = self._cached_tokens[self.request.session['localToken']]
        return User('fogbow', federationToken, self.DEFAULT_FOGBOW_NAME, {}, localToken)
  
    def authenticate(self, request, localCredentials, federationCredentials,
                      localEndpoint=None, federationEndpoint=None):
        tokenStr,localTokenStr = '',''
                  
        # Todo Refator
        federationFormType = settings.FOGBOW_FEDERATION_AUTH_TYPE
        if federationFormType == fogbow_models.IdentityPluginConstants.AUTH_TOKEN:
            tokenStr = federationCredentials[federationFormType]
            x = {'x': tokenStr}
            tokenStr = x['x'].replace('\r\n', '')
        elif federationFormType == fogbow_models.IdentityPluginConstants.AUTH_VOMS:
            tokenStr = federationCredentials[federationFormType]
            x = {'x': tokenStr}
            tokenStr = x['x'].replace('\r\n', '')
        elif federationFormType == fogbow_models.IdentityPluginConstants.AUTH_OPENNEBULA:
            tokenStr = getToken(federationEndpoint, federationCredentials, federationFormType)     
        elif federationFormType == fogbow_models.IdentityPluginConstants.AUTH_KEYSTONE:
            tokenStr = getToken(federationEndpoint, federationCredentials, 'openstack')                        
        
        # Method
        emptyValuesLocalCredentials = True
        for key in localCredentials.keys():
            if localCredentials[key] != '':
                emptyValuesLocalCredentials = False                
        
        # Todo Refator
        localFormType = ''
        if emptyValuesLocalCredentials == False:
            localFormType = settings.FOGBOW_LOCAL_AUTH_TYPE
            if localFormType == fogbow_models.IdentityPluginConstants.AUTH_TOKEN:
                localTokenStr = federationCredentials[federationFormType]
                x = {'x': tokenStr}
                localTokenStr = x['x'].replace('\r\n', '')
            elif localFormType == fogbow_models.IdentityPluginConstants.AUTH_VOMS :
                localTokenStr = federationCredentials[federationFormType]
                x = {'x': tokenStr}
                localTokenStr = x['x'].replace('\r\n', '')
            elif localFormType == fogbow_models.IdentityPluginConstants.AUTH_OPENNEBULA:
                localTokenStr = getToken(localEndpoint, localCredentials, localFormType) 
            elif localFormType == fogbow_models.IdentityPluginConstants.AUTH_KEYSTONE:
                localTokenStr = getToken(localEndpoint, localCredentials, 'openstack')                       
        else:
            localTokenStr = tokenStr
                        
        federatioToken = Token(tokenStr)
        localToken = Token(localTokenStr)                
        
        user = User('', federatioToken, '', {}, localToken=localToken)
                                  
        if fogbow_models.checkUserAuthenticated(localToken) == False:
            user.errors = True
            user.typeError = fogbow_models.getErrorMessage(settings.FOGBOW_LOCAL_AUTH_TYPE)
        
        if fogbow_models.checkUserAuthenticated(federatioToken) == False:
            user.errors = True
            user.typeError = fogbow_models.getErrorMessage(settings.FOGBOW_FEDERATION_AUTH_TYPE)                
        
        request.user = user
        federation_token_id = uuid.uuid4()
        local_token_id = uuid.uuid4()
        request.session['token'] = federation_token_id
        request.session['localToken'] = local_token_id
        self._cached_tokens[federation_token_id] = federatioToken
        self._cached_tokens[local_token_id] = localToken
        return user
      
    def get_group_permissions(self, user, obj=None):
        return set()
  
    def get_all_permissions(self, user, obj=None):
        return set()
  
    def has_perm(self, user, perm, obj=None):
        return False
  
    def has_module_perms(self, user, app_label):
        return False
      
def getToken(endpoint, credentials, type):            
    credentialsStr = '' 
    for key in credentials.keys():
        credentialsStr += '-D%s=%s ' % (key, credentials[key])
      
    command = '%s token --create -DauthUrl=%s %s --type %s' % (FOGBOW_CLI_JAVA_COMMAND, endpoint,
                                                                credentialsStr, type)
    
    reponseStr = commands.getoutput(command)    
  
    if fogbow_models.isResponseOk(reponseStr) == False:        
        return 'None'
      
    return reponseStr

# class FogbowBackend(object):
#  
#     DEFAULT_FOGBOW_NAME = 'Fogbow User'
#  
#     def check_auth_expiry(self, user, margin=None):
#         return True
#  
#     def get_user(self, user_id):     
#         token = self.request.session['token']
#         return User('fogbow', token, self.DEFAULT_FOGBOW_NAME, {})
#  
#     def authenticate(self, request, formType, credentials=None, endpoint=None):
#         tokenStr = ''
#          
#         if formType == form_fogbow.FORM_TYPE_TOKEN:
#             tokenStr = credentials[formType]
#         elif formType == form_fogbow.FORM_TYPE_VOMS :
#             tokenStr = credentials[formType]
#         elif formType == form_fogbow.FORM_TYPE_OPENNEBULA:
#             tokenStr = getToken(endpoint, credentials, formType)            
#          
#         token = Token(tokenStr)
#          
#         user = User('', token, '', {})                                   
#                  
#         if fogbow_models.checkUserAuthenticated(token) == False:
#             user.errors = True
#          
#         request.user = user
#         request.session['token'] = token
#         return user
#      
#     def get_group_permissions(self, user, obj=None):
#         return set()
#  
#     def get_all_permissions(self, user, obj=None):
#         return set()
#  
#     def has_perm(self, user, perm, obj=None):
#         return False
#
#     def has_module_perms(self, user, app_label):
#         return False
    
def getToken(endpoint, credentials, type):            
    credentialsStr = '' 
    for key in credentials.keys():
        credentialsStr += '-D%s=%s ' % (key, credentials[key])
     
    command = '%s token --create -DauthUrl=%s %s --type %s' % (FOGBOW_CLI_JAVA_COMMAND, endpoint,
                                                                credentialsStr, type)
     
    reponseStr = commands.getoutput(command)    
 
    if fogbow_models.isResponseOk(reponseStr) == False:        
        return 'None'
     
    return reponseStr

# Openstack_auth

KEYSTONE_CLIENT_ATTR = "_keystoneclient"

class KeystoneBackend(object):

    def check_auth_expiry(self, auth_ref, margin=None):
        if not utils.is_token_valid(auth_ref, margin):
            msg = _("The authentication token issued by the Identity service "
                    "has expired.")
            LOG.warning("The authentication token issued by the Identity "
                        "service appears to have expired before it was "
                        "issued. This may indicate a problem with either your "
                        "server or client configuration.")
            raise exceptions.KeystoneAuthException(msg)
        return True

    def get_user(self, user_id):
        if (hasattr(self, 'request') and
                user_id == self.request.session["user_id"]):
            token = self.request.session['token']
            endpoint = self.request.session['region_endpoint']
            services_region = self.request.session['services_region']
            user = auth_user.create_user_from_token(self.request, token,
                                                    endpoint, services_region)
            return user
        else:
            return None

    def authenticate(self, request=None, username=None, password=None,
                     user_domain_name=None, auth_url=None, tenantName=None):
        """Authenticates a user via the Keystone Identity API."""
        LOG.debug('Beginning user authentication for user "%s".' % username)

        insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
        ca_cert = getattr(settings, "OPENSTACK_SSL_CACERT", None)
        endpoint_type = getattr(
            settings, 'OPENSTACK_ENDPOINT_TYPE', 'publicURL')

        if utils.get_keystone_version() >= 3:
            if utils.has_in_url_path(auth_url, "/v2.0"):
                LOG.warning("The settings.py file points to a v2.0 keystone "
                            "endpoint, but v3 is specified as the API version "
                            "to use. Using v3 endpoint for authentication.")
                auth_url = utils.url_path_replace(auth_url, "/v2.0", "/v3", 1)

        keystone_client = utils.get_keystone_client()
        try:
            client = keystone_client.Client(
                user_domain_name=user_domain_name,
                username=username,
                password=password,
                auth_url=auth_url,
                insecure=insecure,
                cacert=ca_cert,
                debug=settings.DEBUG)

            unscoped_auth_ref = client.auth_ref
            unscoped_token = auth_user.Token(auth_ref=unscoped_auth_ref)
        except (keystone_exceptions.Unauthorized,
                keystone_exceptions.Forbidden,
                keystone_exceptions.NotFound) as exc:
            msg = _('Invalid user name or password.')
            
            LOG.debug(str(exc))
            raise exceptions.KeystoneAuthException(msg)
        except (keystone_exceptions.ClientException,
                keystone_exceptions.AuthorizationFailure) as exc:
            msg = _("An error occurred authenticating. "
                    "Please try again later.")
            LOG.debug(str(exc))
            raise exceptions.KeystoneAuthException(msg)

        self.check_auth_expiry(unscoped_auth_ref)

        if unscoped_auth_ref.project_scoped:
            auth_ref = unscoped_auth_ref
        else:
            try:
                if utils.get_keystone_version() < 3:
                    projects = client.tenants.list()
                else:
                    client.management_url = auth_url
                    projects = client.projects.list(
                        user=unscoped_auth_ref.user_id)                
            except (keystone_exceptions.ClientException,
                    keystone_exceptions.AuthorizationFailure) as exc:
                msg = _('Unable to retrieve authorized projects.')
                raise exceptions.KeystoneAuthException(msg)

            if not projects:
                msg = _('You are not authorized for any projects.')
                raise exceptions.KeystoneAuthException(msg)

            
            projectFound = False
            while projects:
                project = projects.pop()
                if tenantName == project.name:
                    projectFound = True             
                    try:
                        client = keystone_client.Client(
                            tenant_id=project.id,
                            token=unscoped_auth_ref.auth_token,
                            auth_url=auth_url,
                            insecure=insecure,
                            cacert=ca_cert,
                            debug=settings.DEBUG)
                        auth_ref = client.auth_ref
                        break
                    except (keystone_exceptions.ClientException,
                            keystone_exceptions.AuthorizationFailure):
                        auth_ref = None
            
            if projectFound == False:
                msg = _("Invalid tenant.")
                raise exceptions.KeystoneAuthException(msg)            

            if auth_ref is None:
                msg = _("Unable to authenticate to any available projects.")
                raise exceptions.KeystoneAuthException(msg)
    
        self.check_auth_expiry(auth_ref)
        
        user = auth_user.create_user_from_token(
            request,
            auth_user.Token(auth_ref),
            client.service_catalog.url_for(endpoint_type=endpoint_type))        
        
        if request is not None:
            request.session['unscoped_token'] = unscoped_token.id
            request.user = user

            setattr(request, KEYSTONE_CLIENT_ATTR, client)

        LOG.debug('Authentication completed for user "%s".' % username)
        return user

    def get_group_permissions(self, user, obj=None):
        return set()

    def get_all_permissions(self, user, obj=None):

        if user.is_anonymous() or obj is not None:
            return set()

        role_perms = set(["openstack.roles.%s" % role['name'].lower()
                          for role in user.roles])
        service_perms = set(["openstack.services.%s" % service['type'].lower()
                             for service in user.service_catalog
                             if user.services_region in
                             [endpoint.get('region', None) for endpoint
                              in service.get('endpoints', [])]])
        return role_perms | service_perms

    def has_perm(self, user, perm, obj=None):
        """Returns True if the given user has the specified permission."""
        if not user.is_active:
            return False
        return perm in self.get_all_permissions(user, obj)

    def has_module_perms(self, user, app_label):
        if not user.is_active:
            return False
        for perm in self.get_all_permissions(user):
            if perm[:perm.index('.')] == app_label:
                return True
        return False
