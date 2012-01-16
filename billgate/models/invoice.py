from mongoengine import (
    DateTimeField,
    Document,
    EmailField,
    IntField,
    ReferenceField,
    StringField,
    signals
)
from billgate.models import User
from datetime import datetime

class Invoice(Document):
    name = StringField(max_length=80, required=True)
    email = EmailField(required=True)
    telephone = StringField(max_length=20, required=True)
    date = DateTimeField(required=True)
    user = ReferenceField(User)
    refno = StringField(max_length=80, required=True)
    amount = IntField(min_value=0, required=True)
    description = StringField(max_length=80, required=True)
    
    billing_address1 = StringField(max_length=500, required=True)
    billing_address2 = StringField(max_length=500, required=True)
    billing_city = StringField(max_length=80, required=True)
    billing_state = StringField(max_length=80, required=True)
    billing_country = StringField(max_length=2, required=True)

    shipping_address1 = StringField(max_length=500, required=True)
    shipping_address2 = StringField(max_length=500, required=True)
    shipping_city = StringField(max_length=80, required=True)
    shipping_state = StringField(max_length=80, required=True)
    shipping_country = StringField(max_length=2, required=True)
    
    created_at = DateTimeField(default=datetime.now, required=True)
    updated_at = DateTimeField(required=True)

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        document.updated_at = datetime.now()
    
signals.pre_save.connect(Invoice.pre_save, sender=Invoice)
