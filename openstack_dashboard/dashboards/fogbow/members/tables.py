from django.utils.translation import ugettext_lazy as _

from horizon import tables

class MembersTable(tables.DataTable):
    idMember = tables.Column("idMember", verbose_name=_("Member ID")) 
    cpuIdle = tables.Column("cpuIdle", verbose_name=_("CPU Quota"))
    cpuInUse = tables.Column("cpuInUse", verbose_name=_("CPU In Use"))
    memIdle = tables.Column("memIdle", verbose_name=_("Mem Quota"))
    memInUse = tables.Column("memInUse", verbose_name=_("Mem In Use"))
    flavors = tables.Column("flavors", verbose_name=_("Flavors"))

    class Meta:
        name = "members"
        verbose_name = _("Members")