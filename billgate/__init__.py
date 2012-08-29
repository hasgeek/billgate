# -*- coding: utf-8 -*-

# The imports in this file are order-sensitive
import re

from flask import Flask, Markup, escape
from flask.ext.assets import Environment, Bundle
from baseframe import baseframe, baseframe_js, baseframe_css
from flask.ext.lastuser import LastUser
import coaster.app

# First, make an app

app = Flask(__name__, instance_relative_config=True)
lastuser = LastUser()

#Prepare assets

assets = Environment(app)
js = Bundle(baseframe_js,
            filters='jsmin', output='js/packed.js')
css = Bundle(baseframe_css, 'css/app.css')

# Configure the app
def init_for(env):
    coaster.app.init_app(app, env)
    lastuser.init_app(app)
    assets.register('js_all', js)
    assets.register('css_all', css)

# Last, after config, import the models and views

app.register_blueprint(baseframe)
import billgate.models
import billgate.views


EMAIL_RE = re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}\b', re.I)


def scrubemail(data, rot13=False, css_junk=None):
    """
    Convert email addresses in text into HTML links,
    and optionally obfuscate them with ROT13 and empty CSS classes,
    to hide from spambots.
    """

    def convertemail(m):
        aclass = ' class="rot13"' if rot13 else ''
        email = m.group(0)
        link = 'mailto:' + email
        if rot13:
            link = link.decode('rot13')
        if css_junk and len(email) > 3:
            third = int(len(email) / 3)
            parts = (email[:third], email[third:third * 2], email[third * 2:])
            if isinstance(css_junk, (tuple, list)):
                css_dirty, css_clean = css_junk
                email = '<span class="%s">%s</span><span class="%s">no</span>'\
                    '<span class="%s">%s</span><span class="%s">spam</span>'\
                    '<span class="%s">%s</span>' % (
                    css_clean, parts[0], css_dirty, css_clean, parts[1],
                    css_dirty, css_clean, parts[2])
            else:
                email = '%s<span class="%s">no</span>%s<span class="%s">spam</span>%s' % (
                    parts[0], css_junk, parts[1], css_junk, parts[2])
            email = email.replace('@', '&#64;')
        if rot13:
            return '<a%s data-href="%s">%s</a>' % (aclass, link, email)
        else:
            return '<a%s href="%s">%s</a>' % (aclass, link, email)
    data = EMAIL_RE.sub(convertemail, data)
    return data


@app.template_filter('scrubemail')
def scrubemail_filter(data, css_junk=''):
    return Markup(scrubemail(unicode(escape(data)), rot13=True, css_junk=css_junk))

