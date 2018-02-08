import netaddr
import requests
import base64
import logging
import re

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
from openstack_dashboard.dashboards.fogbow.federated_network.models import FederatedNetwork
from openstack_dashboard.dashboards.fogbow.members.views import IndexView as member_views
from openstack_dashboard.dashboards.fogbow.network.views import IndexView as network_views

LOG = logging.getLogger(__name__)

MEMBER_TERM = fogbow_models.FogbowConstants.MEMBER_TERM
X_OCCI_LOCATION = fogbow_models.FogbowConstants.X_OCCI_LOCATION
FEDERATED_NETWORK_TERM = fogbow_models.FogbowConstants.FEDERATED_NETWORK_TERM
FEDERATED_NETWORK_WITH_VERBOSE = fogbow_models.FogbowConstants.FEDERATED_NETWORK_WITH_VERBOSE
FEDERATED_NETWORK_LABEL = "occi.federatednetwork.label"
FEDERATED_NETWORK_CIDR = "occi.federatednetwork.cidr"
FEDERATED_NETWORK_MEMBERS = "occi.federatednetwork.members"

class JoinMember(forms.SelfHandlingForm):
    
    federated_networks = forms.ChoiceField(label=_('Federated network'), help_text=_('Federated network'), required=False)
        
    members = forms.MultipleChoiceField(label=_('Members'),
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

        self.fields['members'].choices = membersChoices 
        LOG.info(membersChoices)   
        
        federared_network_choices = []
        try:
            federated_networks = self.get_data()
            LOG.info("Federated networks retrieved")
            LOG.info(federated_networks)
            for federated_network in federated_networks:
                federared_network_choices.append((federated_network.get('id'), federated_network.get('label')))
        except Exception as error:
            LOG.error("An error occured while collecting federated networks.")
            LOG.error(error)
        self.fields['federated_networks'].choices = federared_network_choices

    def get_data(self):
        response = fogbow_models.doRequest('get', FEDERATED_NETWORK_WITH_VERBOSE, None, self.request)
        LOG.info(response.text)
        if response is None:
            return []
        elif response.status_code is None or response.status_code >= 400:
            LOG.debug("Response from Federated Network was " + str(response.status_code))
            return []
        else:
            return self.getFederatedNetworkList(response.text)

    def getFederatedNetworkList(self, responseStr):
        LOG.info(responseStr)
        federatedList = []
        fragments = responseStr.split("\n")
        for frag in fragments:
            federated = {}
            LOG.info(frag)
            try:
                federated["id"] = re.search("verbose=true/([0-9a-fA-F\\-]*)", frag).group(1)
                federated["federatedNetworkId"] = re.search("verbose=true/([0-9a-fA-F\\-]*)", frag).group(1)
                federated["label"] = re.search(FEDERATED_NETWORK_LABEL + "=([a-z A-Z]*)", frag).group(1)
                federated["cidr"] = re.search(FEDERATED_NETWORK_CIDR + "=([0-9\\./]*)", frag).group(1)
                federated["members"] = re.search(FEDERATED_NETWORK_MEMBERS + "=([ ,a-zA-Z\\.]*)", frag).group(1)
                LOG.info(FederatedNetwork(federated))
                federatedList.append(FederatedNetwork(federated))
            except Exception:
                LOG.error("Malformed response for Federated Resource")
        LOG.info(federatedList)
        return federatedList
        
    def handle(self, request, data):
        try:
            return shortcuts.redirect(reverse("horizon:fogbow:federated_network:index"))    
        except Exception:
            redirect = reverse("horizon:fogbow:federated_network:index")
            exceptions.handle(request, _('Unable to join members.'), redirect=redirect)         