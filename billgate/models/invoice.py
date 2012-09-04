from decimal import Decimal
from datetime import datetime

from billgate import app
from billgate.models import db, BaseScopedIdNameMixin
from billgate.models.user import User
from billgate.models.workspace import Workspace

__all__ = ['INVOICE_STATUS', 'Invoice']

# --- Constants ---------------------------------------------------------------

class INVOICE_STATUS:
    STUB = 0
    DRAFT = 1
    PROFORMA = 2
    REVIEW = 3
    ACCEPTED = 4
    REJECTED = 5
    WITHDRAWN = 6
    DUE = 7
    OVERDUE = 8
    PAID = 9

# --- Models ------------------------------------------------------------------

class Invoice(BaseScopedIdNameMixin, db.Model):
    """
    Invoices can be in Proforma, Pending or Paid state.
    Invoices should be moved to pendind state after the payment has been made, else they carry tax liabilities.
    """
    __tablename__ = 'invoice'

    workspace_id = db.Column(db.Integer, db.ForeignKey('workspace.id'), nullable=False)
    workspace = db.relation(Workspace, backref=db.backref('invoices', cascade='all, delete-orphan'))
    parent = db.synonym('workspace')

    #: User who submitted the report
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship(User, primaryjoin=user_id == User.id,
        backref=db.backref('invoices', cascade='all, delete-orphan'))
    
    #: will update each time Invoice changes status
    datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    #: may contain payment terms
    description = db.Column(db.Text, nullable=False, default=u'')

    #: may be different from workspace currency
    currency = db.Column(db.Unicode(3), nullable=False, default=u'INR')

    #: Reviewer
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    reviewer = db.relationship(User, primaryjoin=reviewer_id == User.id,
        backref=db.backref('reviewed_invoices', cascade='all'))  # No delete-orphan
    #: Reviewer notes
    notes = db.Column(db.Text, nullable=False, default=u'')  # HTML notes

    #: pending state carries tax liabilities for the generating organization
    status = db.Column(db.Integer, default=INVOICE_STATUS.DRAFT, nullable=False)

    total_value = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.0'))

    __table_args__ = (db.UniqueConstraint('url_id', 'workspace_id'),)

    def update_total_value(self):
        for l in self.line_items:
            print l.description, l.quantity, l.line_total
        self.total_value = sum([l.line_total for l in self.line_items])

    @classmethod
    def getw(cls, workspace):
        return cls.query.filter_by(workspace=workspace).order_by('datetime')

    @classmethod
    def get_by_id(cls, workspace, id):
        return cls.query.filter_by(workspace=workspace, id=id).first()


