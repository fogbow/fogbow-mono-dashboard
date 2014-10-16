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
import openstack_dashboard.models as fogbow_request    
                
COMPUTE_TERM = '/compute/'
STATE_TERM = 'occi.compute.state'
SHH_PUBLIC_KEY_TERM = 'org.fogbowcloud.request.ssh-public-address'
CONSOLE_VNC_TERM = 'org.openstack.compute.console.vnc'
MEMORY_TERM = 'occi.compute.memory'
CORES_TERM = 'occi.compute.cores'
IMAGE_SCHEME = 'http://schemas.openstack.org/template/os#'                
                
class InstanceDetailTab2(tabs.Tab):
    name = _("Instance Details")
    slug = "instance_details"
    template_name = ("fogbow/instance/_detail_instance.html")

    def get_context_data(self, request):
        instance_id = self.tab_group.kwargs['instance_id']    
        response = fogbow_request.doRequest('get', COMPUTE_TERM  + instance_id, None, request)

        instanceDetails = response.text.split('\n')
        state,sshPublic,console_vnc,memory,cores,image  = '-', '-', '-', '-', '-', 'fogbow-image'
        for detail in instanceDetails:
            if STATE_TERM in detail:
                state = self.normalizeAttributes(detail, STATE_TERM)
            elif SHH_PUBLIC_KEY_TERM in detail:
                sshPublic = self.normalizeAttributes(detail, SHH_PUBLIC_KEY_TERM)
            elif MEMORY_TERM in detail:
                memory = self.normalizeAttributes(detail, MEMORY_TERM)
            elif CORES_TERM in detail:
                cores = self.normalizeAttributes(detail, CORES_TERM)
            elif IMAGE_SCHEME in detail:
                image = self.getFeatureInCategoryPerScheme('title', detail)
        
        if instance_id == 'null':
            instance_id = '-'
        
        instance = {'instanceId': instance_id , 'state': state, 'sshPublic':sshPublic,
                     'extra' : instanceDetails,'memory' : memory,
                     'cores' : cores, 'image' : image}
        return {'instance': instance}
    
    def normalizeAttributes(self, propertie, term):
        try:
            return propertie.split(term)[1].replace('=', '').replace('"', '')
        except:
            return ''
        
    def getFeatureInCategoryPerScheme(self, featureName, features):
        features = features.split(';')
        for feature in features:
            print feature
            if featureName in feature:
                return feature.replace(featureName + '=', '') \
                              .replace('"','').replace('Image:','')
        return ''                
                
class InstanceDetailTabs2(tabs.TabGroup):
    slug = "instance_details"
    tabs = (InstanceDetailTab2,)
