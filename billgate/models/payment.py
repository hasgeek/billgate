from billgate.models import db, BaseMixin
from billgate.models.transaction import Transaction
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

    status = db.Column(db.Integer, nullable=False, default=PAYMENT_STATUS.INITIATED)

    response = db.Column(db.Unicode(1200), default=u'', nullable=True)


    def _get_responseAsDict(self):
        if self.response:
            return eval(self.response)
        else:
            return {} # be careful with None and empty dict

    def _set_responseAsDict(self, value):
        if value:
            self.response = str(value)
        else:
            self.response = None

    response = property(_get_responseAsDict, _set_responseAsDict)
