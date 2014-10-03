import hashlib
import logging
import requests

from django.conf import settings
from django.contrib.auth import models

from keystoneclient import exceptions as keystone_exceptions
from openstack_auth import utils

LOG = logging.getLogger(__name__)

def set_session_from_user(request, user):
    request.session['token'] = user.token
    request.session['user_id'] = user.id
    request._cached_user = user
    request.user = user

class User(models.AnonymousUser):
    def __init__(self, id=None, token=None, username=None):
        self.id = id
        self.token = token
        self.username = username

    def __unicode__(self):
        return self.username

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.username)

    @property
    def is_active(self):
        return True

    @property
    def is_superuser(self):
        return True

    def is_authenticated(self, margin=None):        
        return True

def doRequest(method, endpoint, additionalHeaders, token):
    headers = {'content-type': 'text/occi', 'X-Auth-Token' : token}
    if additionalHeaders is not None:
        headers.update(additionalHeaders)    
        
    responseStr, response = '', ''
    try:
        if method == 'get': 
            response = requests.get(settings.MY_ENDPOINT + endpoint, headers=headers)
        elif method == 'delete':
            response = requests.delete(settings.MY_ENDPOINT + endpoint, headers=headers)
        elif method == 'post':        
            response = requests.post(settings.MY_ENDPOINT + endpoint, headers=headers)
        responseStr = response.text
    except Exception:
        raise ConnectionException()
        
    if 'Unauthorized' in responseStr:
        raise horizon.exceptions.NotAuthorized()
    elif 'Bad Request' in responseStr:
        raise BadRequestException()
    
    return response    

class BadRequestException(Exception):
    
  def __init__(self):
    Exception.__init__(self)    
    
class ConnectionException(Exception):
    
  def __init__(self):
    Exception.__init__(self)        
