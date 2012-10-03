from decimal import Decimal
from billgate.models import db, BaseMixin
from billgate.models.invoice import Invoice


__all__ = ['LineItem']


class LineItem(BaseMixin, db.Model):
    """
    A LineItem is part of an invoice.
    Each line item carries an item category, quantity, charged amount, tax rate & line total.
    """
    __tablename__ = 'lineitem'

    #: Invoice to which this line item belongs
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    invoice = db.relationship(Invoice, primaryjoin=invoice_id == Invoice.id,
        backref=db.backref('lineitems', cascade='all, delete-orphan'))

    category_id = db.Column(db.Integer, nullable=False)

    #should include event name and category description
    description = db.Column(db.Unicode(1200), default=u'', nullable=False)

    pat = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.0'))
    quantity = db.Column(db.Integer, default=1, nullable=False)
    tax_rate = db.Column(db.Numeric(2, 2), nullable=False, default=Decimal('0.0'))
    total = db.Column(db.Numeric(10, 2), nullable=True)

    #: which app created/sent this line item for invoicing, default should be self
    source = db.Column(db.Unicode(80), default=u'', nullable=False)

    def update_total(self):
        self.total = self.quantity * self.pat
