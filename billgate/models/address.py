from billgate.models import User

from mongoengine import (
    DateTimeField,
    Document,
    ReferenceField,
    signals,
    StringField,
)
from mongoengine import signals
from uuid import uuid4
from datetime import datetime

class Address(Document):
    name = StringField(max_length=80, required=True)
    hashkey = StringField(max_length=32, required=True, default=uuid4().hex)
    address1 = StringField(max_length=500, required=True)
    address2 = StringField(max_length=500, required=True)
    city = StringField(max_length=80, required=True)
    state = StringField(max_length=80, required=True)
    postal_code = StringField(max_length=50, required=True)
    country = StringField(max_length=3, required=True)
    phone = StringField(max_length=50, required=True)
    user = ReferenceField(User)
    
    created_at = DateTimeField(default=datetime.now, required=True)
    updated_at = DateTimeField(required=True)
    
    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        document.updated_at = datetime.now()
    
signals.pre_save.connect(Address.pre_save, sender=Address)
