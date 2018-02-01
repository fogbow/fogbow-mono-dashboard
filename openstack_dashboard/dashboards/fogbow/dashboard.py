from django.utils.translation import ugettext_lazy as _

import horizon

class MainPanel(horizon.PanelGroup):
    slug = "fogbow-group"
    name = _("User panel")
    panels = ('members', 'request', 'instance', 'storage', 'network', 'attachment', 'usage', 'overview', 'overvieww')       

class Fogbow(horizon.Dashboard):
    name = _("Federation")
    slug = "fogbow"
    panels = ( MainPanel, ) 
    default_panel = 'members'

horizon.register(Fogbow)
