#!/usr/bin/env python
from billgate import app
from billgate.models import db
db.create_all()
app.run('0.0.0.0', port=80)
