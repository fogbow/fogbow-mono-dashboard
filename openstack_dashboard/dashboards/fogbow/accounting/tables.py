from django.utils.translation import ugettext_lazy as _

from horizon import tables

class AccountingTable(tables.DataTable):
    idMember = tables.Column("idMember", verbose_name=_("Member ID")) 
    donated = tables.Column("donated", verbose_name=_("Donated to (FCU*min)"))
    consumed = tables.Column("consumed", verbose_name=_("Cosumed from (FCU*min)"))
    debit = tables.Column("debit", verbose_name=_("Debt"))

    class Meta:
        name = "accounting"
        verbose_name = _("Accounting")