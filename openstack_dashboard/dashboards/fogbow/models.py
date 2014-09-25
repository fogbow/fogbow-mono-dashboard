"""
Stub file to work around django bug: https://code.djangoproject.com/ticket/7198
"""

from django.conf import settings
import requests

def doRequest(method, endpoint, headers):
    headers = {'content-type': 'text/occi', 'X-Auth-Token' : settings.MY_TOKEN} 
    headers.update(headers)
        
    if method == 'get': 
        response = requests.get(settings.MY_ENDPOINT + endpoint, headers=headers)
    elif method == 'delete':
        response = requests.delete(settings.MY_ENDPOINT + endpoint, headers=headers)
    elif method == 'post':        
        response = requests.post(settings.MY_ENDPOINT + endpoint, headers=headers)
    
    return response
