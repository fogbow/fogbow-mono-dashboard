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

import os
import django
import horizon

from django import shortcuts
from django.views.decorators import vary
from openstack_dashboard.models import User
from openstack_dashboard.models import Token
from openstack_dashboard.models import IdentityPluginConstants as IPConstants
from django.contrib.auth.decorators import login_required  # noqa
from django.contrib.auth import views as django_auth_views
from openstack_dashboard import forms
from django.utils import functional
from openstack_dashboard.forms import TokenForm
from openstack_dashboard.forms import OpennebulaForm
from openstack_dashboard.forms import OpenstackForm
from openstack_dashboard.forms import VomsForm
from django.contrib import auth
from openstack_auth import user as auth_user
from openstack_auth import views
from django.utils import functional
from django.template import RequestContext
from horizon import messages
from openstack_auth import forms
from django.contrib.auth import authenticate, login

# AUTH_HORIZON = 'horizon'
# AUTH_TOKEN = 'fogbow authentication'
# AUTH_OPENSTACK = 'keystone'
# AUTH_OPENNEBULA = 'opennebula'
# AUTH_VOMS = 'voms'

def get_user_home(user):
    if user.is_superuser:
        return horizon.get_dashboard('fogbow').get_absolute_url()
    return horizon.get_dashboard('fogbow').get_absolute_url()

@vary.vary_on_cookie
def splash(request):
    if request.user.is_authenticated():
        return shortcuts.redirect(get_user_home(request.user))
    form = forms.Login(request)
    request.session.clear()
    request.session.set_test_cookie()
    
    return shortcuts.render(request, 'splash.html', {'form': form})

@vary.vary_on_cookie
def splash_fogbow(request):
    
    if request.user.is_authenticated():
        return shortcuts.redirect(get_user_home(request.user))     
                 
    request.session.clear()
    request.session.set_test_cookie()
    
    formOption = request.POST.get('form')

    return shortcuts.render(request, 'mysplash2.html', getContextForm(request, formOption))

def myLogin(request, template_name=None, extra_context=None, **kwargs):
    formChosen = request.POST.get('formChosen')
    
    formReference = ''
    if formChosen == IPConstants.AUTH_TOKEN :
        formReference = TokenForm
    elif formChosen == IPConstants.AUTH_OPENSTACK :
        formReference = OpenstackForm
    elif formChosen == IPConstants.AUTH_OPENNEBULA :
        formReference = OpennebulaForm
    elif formChosen == IPConstants.AUTH_VOMS :
        formReference = VomsForm
    
    if formChosen != IPConstants.AUTH_HORIZON:                
        if django.VERSION >= (1, 6):
            form = functional.curry(formReference)
        else:
            form = functional.curry(formReference, request)
        
        if not template_name:
            if request.is_ajax():
                template_name = 'auth/my_login2.html'
                extra_context['hide'] = True
            else:
                template_name = 'auth/login2.html'
                
        if extra_context is None:
            extra_context = {'redirect_field_name': auth.REDIRECT_FIELD_NAME}
            
        extra_context.update(getContextForm(request, formChosen))
        del extra_context['form']               

        print extra_context

        res = django_auth_views.login(request,
                                      template_name=template_name,
                                      authentication_form=form,
                                      extra_context=extra_context,
                                      **kwargs)                
        
        request._cached_user = request.user
        request.user = request.user            
        
        return res
    else:
        return views.login(request)

def getContextForm(request, formOption):
    listForm = {IPConstants.AUTH_TOKEN, IPConstants.AUTH_OPENSTACK, 
                IPConstants.AUTH_OPENNEBULA, IPConstants.AUTH_HORIZON}
                
    formChosen = IPConstants.AUTH_OPENSTACK
    form = OpenstackForm()
    if formOption == IPConstants.AUTH_TOKEN:
        formChosen = IPConstants.AUTH_TOKEN
        form = TokenForm()
    elif formOption == IPConstants.AUTH_OPENSTACK:
        formChosen = IPConstants.AUTH_OPENSTACK
        form = OpenstackForm()
    elif formOption == IPConstants.AUTH_OPENNEBULA: 
        formChosen = IPConstants.AUTH_OPENNEBULA      
        form = OpennebulaForm()
    elif formOption == IPConstants.AUTH_VOMS:
        formChosen = IPConstants.AUTH_VOMS
        form = VomsForm()
    elif formOption == IPConstants.AUTH_HORIZON:
        formChosen = IPConstants.AUTH_HORIZON
        form = forms.Login(request) 
    
    return {'form': form, 'listForm': listForm, 'formChosen': formChosen}
