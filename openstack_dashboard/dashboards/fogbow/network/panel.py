from django.utils.translation import ugettext_lazy as _

import horizon

from openstack_dashboard.dashboards.fogbow import dashboard

class Instance(horizon.Panel):
    name = _("Networks")
    slug = "network"

dashboard.Fogbow.register(Instance)
