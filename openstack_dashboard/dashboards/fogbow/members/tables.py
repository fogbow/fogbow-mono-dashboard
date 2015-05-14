from django.utils.translation import ugettext_lazy as _

from horizon import tables

class MembersTable(tables.DataTable):
    idMember = tables.Column("idMember", verbose_name=_("Member ID")) 
    cpuIdle = tables.Column("cpuIdle", verbose_name=_("Available vCPU quota"))
    cpuInUse = tables.Column("cpuInUse", verbose_name=_("vCPU in use"))
    memIdle = tables.Column("memIdle", verbose_name=_("Available RAM(MB) quota"))
    memInUse = tables.Column("memInUse", verbose_name=_("RAM(MB) in use"))
    InstanceIdle = tables.Column("InstanceIdle", verbose_name=_("Available instances quota"))
    InstanceInUse = tables.Column("InstanceInUse", verbose_name=_("Instances in use"))

    class Meta:
        name = "members"
        verbose_name = _("Members")