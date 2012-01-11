#!/usr/bin/env python

from billgate import app
from billgate.models import db
from os import environ

environ['BILLGATE_ENV'] = 'dev'

db.create_all()
app.config['ASSETS_DEBUG'] = True
app.run('0.0.0.0', 4000, debug=True)
