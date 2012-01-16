from mongoengine import DateTimeField, DictField, Document
from billgate.models import User
from datetime import datetime

class Payment(Document):
    created_at = DateTimeField(default=datetime.now, required=True)
    response = DictField()
