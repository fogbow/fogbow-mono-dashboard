import logging
import commands

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from keystoneclient import exceptions as keystone_exceptions

from openstack_auth import exceptions
from openstack_auth import user as auth_user
from openstack_auth import utils
from openstack_dashboard.models import User
from openstack_dashboard.models import Token
# from openstack_dashboard import backend

LOG = logging.getLogger(__name__)

class FogbowBackend(object):

    def check_auth_expiry(self, auth_ref, margin=None):
        return True

    def get_user(self, user_id):     
        token = self.request.session['token']
        token = self.request.session['token']
        return User('fogbow', token, 'Fogbow User', {})

    def authenticate(self, request, formType, credentials=None, endpoint=None):
        id = 'fogbow'        
        username = 'Fogbow User'
        tokenStr = ''
        
        if formType == 'token' :
            tokenStr = credentials['token']
        elif formType == 'voms' :
            tokenStr = credentials['voms']        
        elif formType == 'openstack' :
            tokenStr = getToken(endpoint, credentials, 'openstack')
        elif formType == 'opennebula' :
            tokenStr = getToken(endpoint, credentials, 'opennebula')            
            
        token = Token(tokenStr)
        
        user = User(id, token, username, {})
        
        if user.is_authenticated() == False:
            user.errors = True                
        
        request.user = user
        request.session['token'] = token
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
    javaCommand = 'java -cp fogbow-cli-0.0.1-SNAPSHOT-jar-with-dependencies.jar org.fogbowcloud.cli.Main $@'            
    
    credentialsStr = '' 
    for key in credentials.keys():
        credentialsStr += '-D%s=%s ' % (key, credentials[key])
    
    command = '%s token --create -DauthUrl=%s %s --type %s' % (javaCommand, endpoint, credentialsStr, type)

    print command
    
    reponseStr = commands.getoutput(command)    
    
    if reponseStr == None or 'Bad Request' in reponseStr or 'Unauthorized' in reponseStr:        
        return 'None'
    
    return reponseStr