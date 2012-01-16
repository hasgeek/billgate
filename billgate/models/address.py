from mongoengine import DateTimeField, Document, ReferenceField, StringField
from billgate.models import User
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
