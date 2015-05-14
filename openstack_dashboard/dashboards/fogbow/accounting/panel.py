from django.utils.translation import ugettext_lazy as _

import horizon

from openstack_dashboard.dashboards.fogbow import dashboard

class Accounting(horizon.Panel):
    name = _("Accounting")
    slug = "accounting"

dashboard.Fogbow.register(Accounting)
