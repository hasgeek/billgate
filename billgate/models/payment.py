from mongoengine import DateTimeField, DictField, Document, signals
from billgate.models import User
from datetime import datetime

class Payment(Document):
    response = DictField()
    
    created_at = DateTimeField(default=datetime.now, required=True)
    updated_at = DateTimeField(required=True)

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        document.updated_at = datetime.now()
    
signals.pre_save.connect(Payment.pre_save, sender=Payment)
