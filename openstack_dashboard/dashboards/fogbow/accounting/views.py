import horizon
import requests
import decimal
import openstack_dashboard.models as fogbow_models

from django.utils.translation import ugettext_lazy as _
from horizon import tables
from horizon import messages
from openstack_dashboard.dashboards.fogbow.accounting.models import Member
from openstack_dashboard.dashboards.fogbow.accounting \
    import tables as project_tables
from openstack_dashboard.dashboards.fogbow.accounting \
    import models as project_models
import math    

MEMBER_TERM = fogbow_models.FogbowConstants.MEMBER_TERM
USAGE_TERM = fogbow_models.FogbowConstants.USAGE_TERM

class IndexView(tables.DataTableView):
    table_class = project_tables.AccountingTable
    template_name = 'fogbow/accounting/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        return context

    def has_more_data(self, table):
        return self._more
    
    def get_data(self):           
        response = fogbow_models.doRequest('get', USAGE_TERM + MEMBER_TERM, None, self.request)   
        
        members = []
        self._more = False
        if response == None:
            return members 
                        
        try:
            responseStr = response.text
            members = self.getMembersList(responseStr);            
        except Exception:
            return members

        return members

    def getMembersList(self, strResponse):
        members = []
        membersList = strResponse.split('\n')
        for m in membersList:
            id, idMember, consumed, donated, balance = '-','0','0','0','0', 
            memberProperties = m.split(',')
            
            for properties in memberProperties: 
                values = properties.split('=')
                value = None
                if len(values) > 1: 
                    value = values[1]                
                if any("memberId" in s for s in values):
                    id = value
                if any("consumed" in s for s in values):
                    consumed = float(value)
                if any("donated" in s for s in values):
                    donated = float(value)                                                
                            
            balance = max(0, (consumed - donated) + math.sqrt(donated))
            
            if id != None:                                                  
                member = {'id': id , 'idMember' : id, 
                          'consumed': "{0:.2f}".format(consumed), 
                          'donated': "{0:.2f}".format(donated), 
                          'debit': "{0:.2f}".format(balance)} 
                members.append(Member(member));
                                            
        return members;
    