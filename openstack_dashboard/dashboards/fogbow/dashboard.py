from django.utils.translation import ugettext_lazy as _

import horizon

class TestPanel(horizon.PanelGroup):
    slug = "mygroup"
    name = _("User Panel")
    panels = ('members', 'request', 'instance')       

class Fogbow(horizon.Dashboard):
    name = _("Fogbow")
    slug = "fogbow"
    panels = ( TestPanel, ) 
    default_panel = 'members'

horizon.register(Fogbow)
