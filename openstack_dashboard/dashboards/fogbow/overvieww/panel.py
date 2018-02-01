from django.utils.translation import ugettext_lazy as _

import horizon

from openstack_dashboard.dashboards.fogbow import dashboard

class Overvieww(horizon.Panel):
    name = _("Overvieww")
    slug = "overvieww"

dashboard.Fogbow.register(Overvieww)
