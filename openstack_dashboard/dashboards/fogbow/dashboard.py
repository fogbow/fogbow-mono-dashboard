from django.utils.translation import ugettext_lazy as _

import horizon

class MainPanel(horizon.PanelGroup):
    slug = "mygroup"
    name = _("User Panel")
    panels = ('overview','members', 'request', 'instance')       

class Fogbow(horizon.Dashboard):
    name = _("Federation")
    slug = "fogbow"
    panels = ( MainPanel, ) 
    default_panel = 'overview'

horizon.register(Fogbow)
