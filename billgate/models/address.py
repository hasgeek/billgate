from mongoengine import Document, StringField

class Address(Document):
    shortname = StringField(max_length=80, required=True)
    address1 = StringField(max_length=500, required=True)
    address2 = StringField(max_length=500, required=True)
    city = StringField(max_length=80, required=True)
    state = StringField(max_length=80, required=True)
    country = StringField(max_length=2, required=True)
