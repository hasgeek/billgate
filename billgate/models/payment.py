from billgate.models import db, BaseMixin
from uuid import uuid4
from datetime import datetime

__all__ = ['Payment', 'PAYMENT_STATUS']

class PAYMENT_STATUS:
    INITIATED = 0
    SUBMITTED = 1
    FAILED = 2
    COMPLETED = 3
    CANCELLED = 4
    REJECTED = 5

class Payment(BaseMixin, db.Model):
    __tablename__ = 'payment'

    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=True)

    status = db.Column(db.Integer, nullable=False, default=PAYMENT_STATUS.SUBMITTED)

    response = db.Column(db.Unicode(1200), default=u'', nullable=True)