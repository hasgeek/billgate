from decimal import Decimal
from datetime import datetime

from flask import url_for

from billgate.models import db, BaseMixin
from billgate.models.workspace import Workspace
from billgate.models.category import Category
from billgate.models.invoice import Invoice


__all__ = ['LineItem']


class LineItem(BaseMixin, db.Model):
    """
    A LineItem is part of an invoice. 
    Each line item carries an item category, quantity, charged amount, tax rate & line total.
    """
    __tablename__ = 'lineitem'
    
    #: Item category of this LineItem
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship(Category, primaryjoin=category_id == Category.id)

    #: Invoice to which this line item belongs
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    invoice = db.relationship(Invoice, primaryjoin=invoice_id == Invoice.id, 
        backref=db.backref('line_items', cascade='all, delete-orphan'))
    
    description = db.Column(db.Unicode(1200), default=u'', nullable=False)
    price_before_tax = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.0'))
    quantity = db.Column(db.Integer, default=1, nullable=False)
    tax_rate = db.Column(db.Numeric(2, 2), nullable=False, default=Decimal('0.0'))
    line_amount_before_tax = db.Column(db.Numeric(10, 2), nullable=True)
    line_total = db.Column(db.Numeric(10, 2), nullable=True)


    def update_line_amount_before_tax(self):
        self.line_amount_before_tax = self.quantity * self.price_before_tax

    def update_line_total(self):
        self.update_line_amount_before_tax()
        self.line_total = self.quantity * self.price_before_tax * (1 + self.tax_rate/100)
