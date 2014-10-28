import horizon
import requests
import decimal
import openstack_dashboard.models as fogbow_request

from django.utils.translation import ugettext_lazy as _  # noqa
from horizon import tables
from horizon import messages
from openstack_dashboard.dashboards.fogbow.members.models import Member
from openstack_dashboard.dashboards.fogbow.members \
    import tables as project_tables
from openstack_dashboard.dashboards.fogbow.members \
    import models as project_models

MEMBER_TERM = fogbow_request.FogbowConstants.MEMBER_TERM

class IndexView(tables.DataTableView):
    table_class = project_tables.MembersTable
    template_name = 'fogbow/members/index.html'
    memTotal, memInUse, memUsedPercentage, cpuTotal, cpuInUse, cpuUsedPercentage = 0,0,0,0,0,0

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['memTotal'] = self.memTotal
        context['memInUse'] = self.memInUse
        context['memUsedPercentage'] = self.memUsedPercentage
        context['cpuTotal'] = self.cpuTotal
        context['cpuInUse'] = self.cpuInUse
        context['cpuUsedPercentage'] = self.cpuUsedPercentage
        return context

    def has_more_data(self, table):
        return self._more
    
    def get_data(self):           
        response = fogbow_request.doRequest('get', MEMBER_TERM, None, self.request)
        
        members = []
        responseStr = response.text
        if fogbow_request.isResponseOk(responseStr) == True:
            members = self.getMembersList(responseStr)    
        
        self._more = False                

        return members
    
    def getMembersList(self, strResponse):
        members = []
        membersList = strResponse.split('\n')
        memInUseTotal,memIdleTotal,cpuIdleTotal,cpuInUseTotal = 0,0,0,0        
        for m in membersList:                
            id, cpuIdle, cpuInUse, flavors, memIdle, memInUse = '-','0','0','','0','0'             
            memberProperties = m.split(';')            
            for properties in memberProperties:
                values = properties.split('=')
                value = None
                if len(values) > 1: 
                    value = values[1]                    
                if any("id" in s for s in values):
                    id = value
                elif any("cpuIdle" in s for s in values): 
                    cpuIdle = float(value)
                elif any("cpuInUse" in s for s in values): 
                    cpuInUse = float(value)
                elif any("memIdle" in s for s in values): 
                    memIdle = float(value)
                elif any("memInUse" in s for s in values):
                    memInUse = float(value)                    
            if 'flavor' in m:
                valuesFlavor = m.split('flavor:')
                for flavor in valuesFlavor:
                   if 'fogbow' in flavor: 
                       flavors = flavors + flavor
                       flavors = flavors.replace("'", '').replace('"', '')                       
                                                
            if id != None:                                                  
                member = {'id': id , 'idMember' : id, 'cpuIdle': cpuIdle, 'cpuInUse': cpuInUse , 'memIdle': memIdle, 'memInUse': memInUse, 'flavors' : flavors}
                members.append(Member(member));                
                
            memInUseTotal += memInUse
            memIdleTotal += memIdle
            cpuIdleTotal += cpuIdle
            cpuInUseTotal += cpuInUse
            
        self.setValuesContext(memIdleTotal, memInUseTotal, cpuIdleTotal, cpuInUseTotal)
        
        return members
    
    def setValuesContext(self, memIdle, memInUse, cpuIdle, cpuInUse):    
        self.memTotal = "{0:.2f}".format(self.convertMbToGb((memIdle + memInUse)))
        self.memInUse = self.convertMbToGb(memInUse)
        self.memUsedPercentage = self.calculatePercentage(memInUse, (memIdle + memInUse))
        self.cpuTotal = "{0:.2f}".format((cpuIdle + cpuInUse))
        self.cpuInUse = cpuInUse 
        self.cpuUsedPercentage = self.calculatePercentage(cpuInUse, (cpuIdle + cpuInUse))
                
    def convertMbToGb(self, value):
        try:
            return float(value / 1024)
        except Exception:
            return 0
    
    def calculatePercentage(self, value, valueTotal):
        try:
            return ((value * 100) / valueTotal)
        except Exception:
            return 0