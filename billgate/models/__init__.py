from flaskext.sqlalchemy import SQLAlchemy
from mongoengine import connect
from billgate import app

connect(app.config['MONGO_DB'], **app.config['MONGO_CONN'])

from billgate.models.user import *
from billgate.models.address import *
from billgate.models.invoice import *
from billgate.models.payment import *
