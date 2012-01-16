#!/usr/bin/env python

from billgate import app
from os import environ

environ['BILLGATE_ENV'] = 'dev'

app.config['ASSETS_DEBUG'] = True
app.run('0.0.0.0', 4000, debug=True)
