# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
from billgate import app
from coaster.sqlalchemy import BaseMixin, BaseNameMixin, BaseScopedNameMixin, BaseScopedIdNameMixin, BaseScopedIdMixin

db = SQLAlchemy(app)

from billgate.models.user import *
from billgate.models.workspace import *
from billgate.models.category import *
from billgate.models.line_item import *
from billgate.models.invoice import *
from billgate.models.address import *
from billgate.models.payment import *
