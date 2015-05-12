from django.utils.translation import ugettext_lazy as _

from horizon import tables

class MembersTable(tables.DataTable):
    idMember = tables.Column("idMember", verbose_name=_("Member id")) 
    cpuIdle = tables.Column("cpuIdle", verbose_name=_("CPU quota"))
    cpuInUse = tables.Column("cpuInUse", verbose_name=_("CPU in use"))
    memIdle = tables.Column("memIdle", verbose_name=_("Mem quota"))
    memInUse = tables.Column("memInUse", verbose_name=_("Mem in use"))
    InstanceInUse = tables.Column("InstanceInUse", verbose_name=_("Instances in use"))
    InstanceIdle = tables.Column("InstanceIdle", verbose_name=_("Instances quota"))

    class Meta:
        name = "members"
        verbose_name = _("Members")