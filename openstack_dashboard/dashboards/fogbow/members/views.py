from horizon import views

import requests

from django.core.urlresolvers import reverse_lazy  # noqa
from django.utils.translation import ugettext_lazy as _  # noqa
from django.conf import settings

from horizon import exceptions
from horizon import tables
from django.http import HttpRequest

import openstack_dashboard.dashboards.fogbow.models as fogbow_request

from openstack_dashboard.dashboards.fogbow.members.models import Member
from openstack_dashboard.dashboards.fogbow.members \
    import tables as project_tables
from openstack_dashboard.dashboards.fogbow.members \
    import models as project_models

class IndexView(tables.DataTableView):
    table_class = project_tables.MembersTable
    template_name = 'fogbow/members/index.html'

    def has_more_data(self, table):
        return self._more
    
    def get_data(self):                    
        response = fogbow_request.doRequest('get', '/members', None)        
        if response.status_code < 200 and response.status_code > 204:
            print 'erro'
        
        strResponse = response.text
        
        members = self.returnMemberList(strResponse)                                 
        self._more = False                
                
        return members
    
    def returnMemberList(self, strResponse):
        members = []        
        membersList = strResponse.split('\n')        
        for m in membersList:                
            id, cpuIdle, cpuInUse, flavors = '-','-','-',''            
            memberProperties = m.split(';')            
            for properties in memberProperties:
                values = properties.split('=')
                value = None
                if len(values) > 1: 
                    value = values[1]
                    
                if any("id" in s for s in values):
                    id = value
                elif any("cpuIdle" in s for s in values): 
                    cpuIdle = value
                elif any("cpuInUse" in s for s in values): 
                    cpuInUse = value
                elif any("memIdle" in s for s in values): 
                    memIdle = value
                elif any("memInUse" in s for s in values):
                    memInUse = value
                    
            if 'flavor' in m:
                valuesFlavor = m.split('flavor:')
                for flavor in valuesFlavor:
                   if 'fogbow' in flavor: 
                       flavors = flavors + flavor
                       flavors = flavors.replace("'", '').replace('"', '').replace(',', " - ").replace(';', ' _ ')                       
                                                
            if id != None:                                                  
                member = {'id': id , 'idMember' : id, 'cpuIdle': cpuIdle, 'cpuInUse': cpuInUse , 'memIdle': memIdle, 'memInUse': memInUse, 'flavors' : flavors}
                members.append(Member(member));                
        
        return members     
