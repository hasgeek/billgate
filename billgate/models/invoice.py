from mongoengine import (
    DateTimeField,
    Document,
    EmailField,
    IntField,
    ListField,
    ReferenceField,
    StringField,
    signals
)
from billgate.models import User
from datetime import datetime

class Invoice(Document):
    name = StringField(max_length=80)
    email = EmailField()
    telephone = StringField(max_length=20)
    date = DateTimeField(required=True)
    user = ReferenceField(User)
    invoice_no = StringField(max_length=80)
    amount = IntField(min_value=0)
    description = StringField(max_length=80)
    lineitems = ListField()
    
    billing_address1 = StringField(max_length=500)
    billing_address2 = StringField(max_length=500)
    billing_city = StringField(max_length=80)
    billing_state = StringField(max_length=80)
    billing_country = StringField(max_length=3)
    billing_postal_code = StringField(max_length=50, required=True)

    shipping_address1 = StringField(max_length=500)
    shipping_address2 = StringField(max_length=500)
    shipping_city = StringField(max_length=80)
    shipping_state = StringField(max_length=80)
    shipping_country = StringField(max_length=3)
    shipping_postal_code = StringField(max_length=50, required=True)
    
    created_at = DateTimeField(default=datetime.now, required=True)
    updated_at = DateTimeField(required=True)

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        document.updated_at = datetime.now()
    
signals.pre_save.connect(Invoice.pre_save, sender=Invoice)
