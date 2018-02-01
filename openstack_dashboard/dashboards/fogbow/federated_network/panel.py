from django.utils.translation import ugettext_lazy as _

import horizon

from openstack_dashboard.dashboards.fogbow import dashboard

class FederatedNetwork(horizon.Panel):
    name = _("Federated Networks")
    slug = "federated_network"

dashboard.Fogbow.register(FederatedNetwork)
