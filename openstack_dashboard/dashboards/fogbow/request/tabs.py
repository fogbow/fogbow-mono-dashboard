# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from django.core.urlresolvers import reverse  # noqa
from django.utils.translation import ugettext_lazy as _  # noqa

from horizon import exceptions
from horizon import tabs
import requests
from django.conf import settings

from openstack_dashboard.api import cinder
from openstack_dashboard.api import nova
import openstack_dashboard.dashboards.fogbow.models as fogbow_request

class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("fogbow/request/_detail_overview.html")

    def get_context_data(self, request):
        instance_id = self.tab_group.kwargs['instance_id']
        instance_id = instance_id.split(':')[1]
        
        response = fogbow_request.doRequest('get', '/compute/' + instance_id, None)

        responseStr = response.text
        instanceDetails = responseStr.split('\n')
        state = 'stateDefault'
        sshPublic = 'sshPublicDefault'
        for d in instanceDetails:
            if 'occi.compute.state' in d:
                d = d.split('occi.compute.state')
                d = d[1]
                d = d.replace('=', '')
                d = d.replace('"', '')
                state = d
            elif 'org.fogbowcloud.request.ssh-public-address' in d:
                d = d.split('org.fogbowcloud.request.ssh-public-address')
                d = d[1]
                d = d.replace('"', '')
                d = d.replace('=', '')
                sshPublic = d
        
        instance = {'instanceId': instance_id , 'state': state, 'sshPublic':sshPublic, 'extra' : instanceDetails}
        return {'instance': instance}

class RequestDetailTabs(tabs.TabGroup):
    slug = "volume_details"
    tabs = (OverviewTab,)
