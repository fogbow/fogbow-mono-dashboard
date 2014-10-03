import logging

from django.conf import settings
from django.contrib.auth import authenticate  # noqa
from django.contrib.auth import forms as django_auth_forms
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables  # noqa

from openstack_auth import exceptions


LOG = logging.getLogger(__name__)


class Login(django_auth_forms.AuthenticationForm):

    region = forms.ChoiceField(label=_("Region"), required=False)
    usernamet = forms.CharField(
        label=_("User Name1"),
        widget=forms.TextInput(attrs={"autofocus": "autofocus"}))
    passwordt = forms.CharField(label=_("Password1"),
                               widget=forms.PasswordInput(render_value=False))