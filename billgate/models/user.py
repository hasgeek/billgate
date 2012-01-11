from mongoengine import Document, StringField


class User(Document):
    name = StringField(max_length=200, required=True)
