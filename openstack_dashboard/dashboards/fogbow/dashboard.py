from django.utils.translation import ugettext_lazy as _

import horizon

class MainPanel(horizon.PanelGroup):
    slug = "fogbow-group"
    name = _("User panel")
    panels = ('overview','members', 'request', 'instance', 'accounting')       

class Fogbow(horizon.Dashboard):
    name = _("Federation")
    slug = "fogbow"
    panels = ( MainPanel, ) 
    default_panel = 'overview'

horizon.register(Fogbow)
