import re

from flask import (Flask, render_template, redirect, url_for, abort, g, Markup,
    escape)
from flaskext.assets import Environment, Bundle
from flaskext.sqlalchemy import SQLAlchemy
# from flaskext.lastuser import LastUser

app = Flask(__name__)
db = SQLAlchemy(app)
assets = Environment(app)
# lastuser = LastUser(app)

# --- Configuration -----------------------------------------------------------

app.config.from_object(__name__)
try:
    app.config.from_object('settings')
except ImportError:
    import sys
    print >> sys.stderr, "Please create a settings.py with the necessary settings. See settings-sample.py."
    sys.exit()


# --- Assets ------------------------------------------------------------------

js = Bundle('js/libs/jquery-1.5.1.min.js',
            'js/libs/jquery.form.js',
            'js/scripts.js',
            filters='jsmin', output='js/packed.js')

assets.register('js_all', js)


# --- Routes ------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'), code=301)


@app.route('/privacy')
def privacy():
    return render_template('privacy.html', title="Privacy Policy")


@app.route('/terms')
def terms():
    return render_template('terms.html', title="Terms & Conditions")


@app.route('/refunds')
def refunds():
    return render_template('refunds.html', title="Cancellation & Refund Policy")


@app.route('/disclaimer')
def disclaimer():
    return render_template('disclaimer.html', title="Disclaimer")


@app.route('/login')
# @lastuser.loginhandler
def login():
    return "Can't login yet"


@app.route('/logout')
# @lastuser.logouthandler
def logout():
    return "You weren't logged in"

# --- Template filters --------------------------------------------------------

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
        if css_junk and len(email)>3:
            third = int(len(email) / 3)
            parts = (email[:third], email[third:third*2], email[third*2:])
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


if __name__ == '__main__':
    app.run(port=4000, debug=True)
