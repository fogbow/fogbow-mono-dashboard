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

from django import shortcuts
from django.views.decorators import vary
from django.contrib.auth.models import User

import cgi
import horizon

from openstack_auth import forms

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

def loginChico(request):        
    field = MyField("Nome")
    visible_field = []
    visible_field.append(field)    
    form = MyForm(visible_field)
    request.session.clear()
    request.session.set_test_cookie()  
    return shortcuts.render(request, 'mysplash.html', {'form': form})

def myauthenticate(request):
    x
#     user = c()
#     username = request.POST['username']
#     username = 'admin'
#     password = request.POST['password']
#     password = 'labstack'
#     
#     user = authenticate(username=username, password=password)
#     if user is not None:
#         if user.is_active:
#             login(request, user)
#         else:
#             x
#     else:
#         y
#     from django.contrib.auth.models import User    
#     user = User.objects.get(username__exact='admin')
    
#     login(request, user)
#     
#     form = ""
#     token = request.POST.get('token', u'Nao existe !')
#     request.session.clear()
#     request.session.set_test_cookie()
#     try:
#         request.session['mytoken'] == "Pow"
#     except Exception:
#         form = forms.Login(request)
#         return shortcuts.render(request, 'splash.html', {'form': form})
#     return shortcuts.render(request, 'mysplash.html', {'form': form})
#     return shortcuts.redirect(horizon.get_dashboard('fogbow').get_absolute_url())
    
# def c():  
#     user = User.create_user('neto', 'neto@thebeatles.com', 'neto')    
#     return user
    
from django.contrib.auth import authenticate, login
    
class MyForm:
    visible_fields = None
    
    def __init__(self, visible_fields):
        self.visible_fields = visible_fields
        
class MyField:
    label_tag = None
    
    def __init__(self, label_tag):
        self.label_tag = label_tag