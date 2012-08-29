# -*- coding: utf-8 -*-

from billgate.models import db, BaseNameMixin

__all__ = ['Workspace']

CURRENCIES = [
    ('INR', 'INR - India Rupee'),
    ('USD', 'USD - US Dollar'),
    ('EUR', 'EUR - Euro'),
    ('GBP', 'GBP - Great Britain Pound'),
    ('SGD', 'SGD - Singapore Dollar'),
    ]


class Workspace(BaseNameMixin, db.Model):
    """
    Workspaces contain categories of items, invoices and payments for a purchase. 
    Workspaces correspond to organizations in LastUser.
    """
    __tablename__ = 'workspace'
    
    userid = db.Column(db.Unicode(22), nullable=False, unique=True)
    currency = db.Column(db.Unicode(3), nullable=False, default=u'INR')
    fullname = db.Column(db.Unicode(250), nullable=False)
    address = db.Column(db.Unicode(1200), nullable=False)
    cin = db.Column(db.Unicode(50), nullable=True)
    tan = db.Column(db.Unicode(50), nullable=True)
    pan = db.Column(db.Unicode(50), nullable=True)
    tin = db.Column(db.Unicode(50), nullable=True)

    @classmethod
    def get(cls, name):
        return cls.query.filter_by(name=name).first()
