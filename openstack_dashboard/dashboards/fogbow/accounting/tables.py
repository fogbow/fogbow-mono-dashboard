from django.utils.translation import ugettext_lazy as _

from horizon import tables

class AccountingTable(tables.DataTable):
    idMember = tables.Column("idMember", verbose_name=_("Member ID")) 
    donated = tables.Column("donated", verbose_name=_("Donated (FCU*min)"))
    consumed = tables.Column("consumed", verbose_name=_("Cosumed (FCU*min)"))
    debit = tables.Column("debit", verbose_name=_("Debit"))

    class Meta:
        name = "accounting"
        verbose_name = _("Accounting")