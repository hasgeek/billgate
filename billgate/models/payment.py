from mongoengine import Document, StringField, IntField, ReferenceField
from billgate.models import User

class Payment(Document):
    name = StringField(max_length=80, required=True)
    email = EmailField(required=True)
    telephone = StringField(max_length=20, required=True)
    user = StringField(max_length=80, required=True)
    date = ReferenceField(User)
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
    
    gateway = StringField(max_length=80, required=True)
    response_code = StringField(max_length=80, required=True)
    response_message = StringField(max_length=80, required=True)
    payment_id = StringField(max_length=80, required=True)
    transaction_id = StringField(max_length=80, required=True)
