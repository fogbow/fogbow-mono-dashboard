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
from openstack_dashboard.forms import VomsForm
from openstack_dashboard.forms import KeystoneFogbow
from django.contrib import auth
from openstack_dashboard import models as auth_user
from openstack_auth import views
from django.template import RequestContext
from horizon import messages
from openstack_auth import forms
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.utils import functional
from django.views.decorators.cache import never_cache  # noqa
from django.views.decorators.csrf import csrf_protect  # noqa
from django.views.decorators.debug import sensitive_post_parameters  # noqa

def get_user_home(user):
    return horizon.get_dashboard('fogbow').get_absolute_url()

@vary.vary_on_cookie
def splash(request):
    if request.user.is_authenticated():
        return shortcuts.redirect(get_user_home(request.user))
    form = KeystoneFogbow()
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

    return shortcuts.render(request, 'fogbow_splash.html',
                             getContextForm(request, formOption))

def myLogin(request, template_name=None, extra_context=None, **kwargs):
    formChosen = request.POST.get('formChosen')
    
    formReference = ''
    if formChosen == IPConstants.AUTH_TOKEN :
        formReference = TokenForm
    elif formChosen == IPConstants.AUTH_OPENNEBULA :
        formReference = OpennebulaForm
    elif formChosen == IPConstants.AUTH_VOMS :
        formReference = VomsForm
    elif formChosen == IPConstants.AUTH_KEYSTONE :
        formReference = KeystoneFogbow        
    
    initial = {}
    if formChosen == IPConstants.AUTH_KEYSTONE:
        if (request.user.is_authenticated() and
            auth.REDIRECT_FIELD_NAME not in request.GET and
            auth.REDIRECT_FIELD_NAME not in request.POST):
            return shortcuts.redirect(settings.LOGIN_REDIRECT_URL)
    
        current_region = request.session.get('region_endpoint', None)
        requested_region = request.GET.get('region', None)
        regions = dict(getattr(settings, 'AVAILABLE_REGIONS', []))
        if requested_region in regions and requested_region != current_region:
            initial.update({'region': requested_region})
    
    if request.method == "POST":                
        if django.VERSION >= (1, 6):
            form = functional.curry(formReference)
        else:
            form = functional.curry(formReference, request)
    else:
        form = functional.curry(formReference, initial=initial)
        
    if not template_name:
        if request.is_ajax():
            template_name = 'auth/fogbow_login.html'
            extra_context['hide'] = True
        else:
            template_name = 'auth/fogbowlogin.html'
            
    if extra_context is None:
        extra_context = {'redirect_field_name': auth.REDIRECT_FIELD_NAME}
        
    extra_context.update(getContextForm(request, formChosen))
    del extra_context['form']               

    res = django_auth_views.login(request,
                                  template_name=template_name,
                                  authentication_form=form,
                                  extra_context=extra_context,
                                  **kwargs)
             
    if formChosen == IPConstants.AUTH_KEYSTONE:
        auth_user.set_session_from_user(request, request.user)
        regions = dict(forms.Login.get_region_choices())
        region = request.user.endpoint
        region_name = regions.get(region)
        request.session['region_endpoint'] = region
        request.session['region_name'] = region_name        
    else:
        request._cached_user = request.user
        request.user = request.user
                    
    return res

def getContextForm(request, formOption):
    listForm = {IPConstants.AUTH_TOKEN, IPConstants.AUTH_OPENNEBULA, 
                IPConstants.AUTH_KEYSTONE}
                
    formChosen = IPConstants.AUTH_KEYSTONE
    form = KeystoneFogbow()
    if formOption == IPConstants.AUTH_TOKEN:
        formChosen = IPConstants.AUTH_TOKEN
        form = TokenForm()
    elif formOption == IPConstants.AUTH_OPENNEBULA: 
        formChosen = IPConstants.AUTH_OPENNEBULA      
        form = OpennebulaForm()
    elif formOption == IPConstants.AUTH_VOMS:
        formChosen = IPConstants.AUTH_VOMS
        form = VomsForm()
    elif formOption == IPConstants.AUTH_KEYSTONE:
        formChosen = IPConstants.AUTH_KEYSTONE
        form = KeystoneFogbow()
    
    return {'form': form, 'listForm': listForm, 'formChosen': formChosen}
