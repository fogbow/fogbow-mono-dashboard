import netaddr
import requests

from django.conf import settings  # noqa
from django.core.urlresolvers import reverse  # noqa
from django.core import validators
from django.forms import ValidationError  # noqa
from django.utils.translation import ugettext_lazy as _  # noqa

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon.utils import fields
from horizon.utils import validators as utils_validators

from openstack_dashboard import api
from openstack_dashboard.utils import filters

import urllib2
import urllib

import collections  

class CreateRequest(forms.SelfHandlingForm):
    count = forms.CharField(label=_("Count"),
                           error_messages={
                               'required': _('This field is required.'),
                               'invalid': _("The string may only contain"
                                            " ASCII characters and numbers.")},
                           validators=[validators.validate_slug])
    flavor = forms.CharField(label=_("Flavor"),
                           error_messages={
                               'required': _('This field is required.'),
                               'invalid': _("The string may only contain"
                                            " ASCII characters and numbers.")},
                           validators=[validators.validate_slug])
    image = forms.CharField(label=_("Image"),
                           error_messages={
                               'required': _('This field is required.'),
                               'invalid': _("The string may only contain"
                                            " ASCII characters and numbers.")},
                           validators=[validators.validate_slug])
    type = forms.CharField(label=_("Type"),
                           error_messages={
                               'required': _('This field is required.'),
                               'invalid': _("The string may only contain"
                                            " ASCII characters and numbers.")},
                           validators=[validators.validate_slug])    
    publicKey = forms.CharField(label=_("Public Key"),
                           error_messages={'invalid': _("The string may only contain"
                                            " ASCII characters and numbers.")})        

    def handle(self, request, data):
        try:            
#             headers = {'content-type': 'text/occi', 'X-Auth-Token' : settings.MY_TOKEN , "Category" : 'fogbow_request; scheme="http://schemas.fogbowcloud.org/request#"; class="kind"', 'Category' : data['flavor'] + '; scheme="http://schemas.fogbowcloud.org/template/resource#"; class="mixin"', 'Category' : data['image']+ '; scheme="http://schemas.fogbowcloud.org/template/os#"; class="mixin"', 'X-OCCI-Attribute' : 'org.fogbowcloud.request.instance-count=' + data['count'], 'X-OCCI-Attribute' : 'org.fogbowcloud.request.type=' + data['type']}            
            headers = [('content-type', 'text/occi'), ('X-Auth-Token' , settings.MY_TOKEN) , ("Category" , 'fogbow_request; scheme="http://schemas.fogbowcloud.org/request#"; class="kind"'), ('Category', data['flavor'] + '; scheme="http://schemas.fogbowcloud.org/template/resource#"; class="mixin"'), ('Category' , data['image']+ '; scheme="http://schemas.fogbowcloud.org/template/os#"; class="mixin"'), ('X-OCCI-Attribute' , 'org.fogbowcloud.request.instance-count=' + data['count']), ('X-OCCI-Attribute' , 'org.fogbowcloud.request.type=' + data['type'])]            
#             headers = {'content-type': 'text/occi', 'X-Auth-Token' : settings.MY_TOKEN , "Category" : 'fogbow_request; scheme="http://schemas.fogbowcloud.org/request#"; class="kind"', 'Category' : data['flavor'] + '; scheme="http://schemas.fogbowcloud.org/template/resource#"; class="mixin"', 'Category' : data['image']+ '; scheme="http://schemas.fogbowcloud.org/template/os#"; class="mixin"', 'X-OCCI-Attribute' : 'org.fogbowcloud.request.instance-count=' + data['count'], 'X-OCCI-Attribute' : 'org.fogbowcloud.request.type=' + data['type']}            
#             headers = {'content-type': 'text/occi', 'X-Auth-Token' : settings.MY_TOKEN, 'Category': ['fogbow_request; scheme="http://schemas.fogbowcloud.org/request#"; class="kind"', data['flavor'] + '; scheme="http://schemas.fogbowcloud.org/template/resource#"; class="mixin"']}
#             self.flatten_headers(headers)
            
#             opener = urllib2.build_opener()
#             opener.addheaders = headers
#             query_args = { 'q':'query string', 'foo':'bar' }
# 
#             url = settings.MY_ENDPOINT + '/fogbow_request'
# 
#             data = urllib.urlencode(query_args)
# 
#             request = urllib2.Request(url, data)
#             
#             r = opener.urlopen(request).read()
            
#             r = opener.read()

#             r = requests.post( settings.MY_ENDPOINT + '/fogbow_request', headers=headers)                                    
            
            messages.error(request, _('Error: %s') % r)
#             if r.status_code != 200:
#                 messages.error(request, _('Error: %s') % r)
#                 messages.error(request, _('Error: %s') % r.text)
#             else:
#                 messages.success(request, _('Successfully created Requests: %s') % r)
#                 messages.success(request, _('Successfully created Requests: %s') % r.text)
        except Exception:
            redirect = reverse("horizon:fogbow:request:index")
            exceptions.handle(request,
                              _('Unable to create Requests.'),
                              redirect=redirect)
            
    def flatten_headers(headers):
        for (k, v) in list(headers.items()):
            if isinstance(v, collections.Iterable):
               headers[k] = ','.join(v)