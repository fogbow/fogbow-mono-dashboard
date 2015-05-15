import horizon
import requests
import decimal
import openstack_dashboard.models as fogbow_models

from django.utils.translation import ugettext_lazy as _
from horizon import tables
from horizon import messages
from openstack_dashboard.dashboards.fogbow.members.models import Member
from openstack_dashboard.dashboards.fogbow.members \
    import tables as project_tables
from openstack_dashboard.dashboards.fogbow.members \
    import models as project_models

MEMBER_TERM = fogbow_models.FogbowConstants.MEMBER_TERM
QUOTA_TERM = fogbow_models.FogbowConstants.QUOTA_TERM
MAX_VALUE = 2000000000

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
        response = fogbow_models.doRequest('get', MEMBER_TERM, None, self.request)
        responseQuota = fogbow_models.doRequest('get', QUOTA_TERM, None, self.request, hiddenMessage=None)   
        
        members = []
        self._more = False
        if response == None:
            return members 
                
        responseStr = response.text
        if fogbow_models.isResponseOk(responseStr) == True:
            responseStr = self.addUserLocalQuota(responseStr, responseQuota)
                    
            members = self.getMembersList(responseStr)                              

        return members
    
    def addUserLocalQuota(self, responseStr, responseQuota):
        if responseQuota != None:
            resposenQuotaStr = responseQuota.text
            username = self.request.session['username']
            newUserQuotaRow = '\n%s;%s' % ('id=%s: %s' % ("Local user", username) , resposenQuotaStr)
            if fogbow_models.isResponseOk(resposenQuotaStr) == True:
                responseStr = responseStr + newUserQuotaRow
        
        return responseStr        
        
    
    def getMembersList(self, strResponse):
        members = []
        membersList = strResponse.split('\n')
        memInUseTotal,memIdleTotal,cpuIdleTotal,cpuInUseTotal = 0,0,0,0
        for m in membersList:
            id, cpuIdle, cpuInUse, memIdle, memInUse, InstanceIdle, InstanceInUse = '-','0','0','0','0','0','0'            
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
                elif any("instancesInUse" in s for s in values):
                    try:
                        InstanceInUse = float(value)
                    except Exception:
                        InstanceInUse = 0
                elif any("instancesIdle" in s for s in values):
                    try:
                        InstanceIdle = float(value)
                    except Exception:
                        InstanceIdle = 0            

            if id != None:                                                  
                member = {'id': id , 'idMember' : id, 
                          'cpuIdle': 'No limit' if cpuIdle > MAX_VALUE else cpuIdle, 
                          'cpuInUse': cpuInUse , 
                          'memIdle': 'No limit' if memIdle > MAX_VALUE else memIdle, 
                          'memInUse': memInUse, 
                          'InstanceInUse' : InstanceInUse,
                          'InstanceIdle' : 'No limit' if InstanceIdle > MAX_VALUE else InstanceInUse}
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
        self.memUsedPercentage = fogbow_models.calculatePercent(memInUse, (memIdle + memInUse))
        self.cpuTotal = "{0:.2f}".format((cpuIdle + cpuInUse))
        self.cpuInUse = cpuInUse 
        self.cpuUsedPercentage = fogbow_models.calculatePercent(cpuInUse, (cpuIdle + cpuInUse))
                
    def convertMbToGb(self, value):
        try:
            return float(value / 1024)
        except Exception:
            return 0
