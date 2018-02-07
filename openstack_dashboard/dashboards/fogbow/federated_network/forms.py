import netaddr
import requests
import base64
import logging

from django import shortcuts
from django.core import validators
from django.core.validators import RegexValidator
from django.core.urlresolvers import reverse 
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _  
from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon.utils import fields
import openstack_dashboard.models as fogbow_models
from openstack_dashboard.dashboards.fogbow.members.views import IndexView as member_views
from openstack_dashboard.dashboards.fogbow.network.views import IndexView as network_views

LOG = logging.getLogger(__name__)

MEMBER_TERM = fogbow_models.FogbowConstants.MEMBER_TERM

class JoinMember(forms.SelfHandlingForm):
    
    federated_networks_fields = forms.ChoiceField(label=_('Federated network'), help_text=_('Federated network'), required=False)
        
    members_fields = forms.MultipleChoiceField(label=_('Members'),
                           widget=forms.CheckboxSelectMultiple, help_text=_('Members'), required=False)    
    
    def __init__(self, request, *args, **kwargs):
        super(JoinMember, self).__init__(request, *args, **kwargs)        
        
        membersChoices = []
        try:
            membersResponseStr = fogbow_models.doRequest('get', MEMBER_TERM, None, request).text
            members = member_views().getMembersList(membersResponseStr)
            for m in members:
                membersChoices.append((m.get('idMember'), m.get('idMember')))
        except Exception as error:
            LOG.error('Error')
            LOG.error(error)
            pass

        self.fields['members_fields'].choices = membersChoices 
        LOG.info(membersChoices)   
        
        federated_networks = []
        federated_networks.append(('one', 'id one'))
        federated_networks.append(('two', 'id two'))
        self.fields['federated_networks_fields'].choices = federated_networks
        
    def handle(self, request, data):
        try:
            return shortcuts.redirect(reverse("horizon:fogbow:federated_network:index"))    
        except Exception:
            redirect = reverse("horizon:fogbow:federated_network:index")
            exceptions.handle(request, _('Unable to join members.'), redirect=redirect)         