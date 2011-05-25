import re

from flask import (Flask, render_template, redirect, url_for, abort, g, Markup,
    escape, flash, request)
from flaskext.assets import Environment, Bundle
from flaskext.sqlalchemy import SQLAlchemy
import flaskext.wtf as wtf
from flaskext.lastuser import LastUser
from flaskext.lastuser.sqlalchemy import UserBase, UserManager

app = Flask(__name__)
db = SQLAlchemy(app)
assets = Environment(app)
lastuser = LastUser()


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

# --- Constants ---------------------------------------------------------------

class ADDRESSTYPE:
    BILLING = 0
    SHIPPING = 1


# --- Models ------------------------------------------------------------------

class User(db.Model, UserBase):
    """
    User object.
    """
    pass


class PostalAddress(db.Model):
    """
    Billing address.
    """
    __tablename__ = 'postaladdress'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship(User, primaryjoin=user_id == User.id, backref='addresses')

    address_type = db.Column(db.Integer, nullable=False, default=ADDRESSTYPE.BILLING)
    label = db.Column(db.Unicode(80), nullable=False, default=u'')
    name = db.Column(db.Unicode(80), nullable=False)
    address = db.Column(db.Unicode(80), nullable=False)
    address2 = db.Column(db.Unicode(80), nullable=False, default=u'')
    address3 = db.Column(db.Unicode(80), nullable=False, default=u'')
    city = db.Column(db.Unicode(30), nullable=False)
    state = db.Column(db.Unicode(30), nullable=False)
    postal_code = db.Column(db.Unicode(10), nullable=False)
    country = db.Column(db.Unicode(30), nullable=False)
    phone = db.Column(db.Unicode(30), nullable=False)
    email = db.Column(db.Unicode(80), nullable=False)


# --- LastUser configuration --------------------------------------------------

lastuser.init_app(app)
lastuser.init_usermanager(UserManager(db, User))

# --- Forms -------------------------------------------------------------------

class PostalAddressForm(wtf.Form):
    name = wtf.TextField('Your name', validators=[wtf.Required()])
    address = wtf.TextField('Address', validators=[wtf.Required()])
    address2 = wtf.TextField('Address')
    address3 = wtf.TextField('Address')
    city = wtf.TextField('City/District', validators=[wtf.Required()])
    state = wtf.TextField('State/Province', validators=[wtf.Required()])
    postal_code = wtf.TextField('Postal code (PIN/ZIP)', validators=[wtf.Required()])
    country = wtf.SelectField('Country', validators=[wtf.Required()], default='IND',
        choices=app.config.get('COUNTRY_LIST', []))
    phone = wtf.TextField('Phone', validators=[wtf.Required()],
        description="The telephone number associated with this address")
    label = wtf.TextField('Label',
        description="Give this address an optional label. If you have multiple addresses, "
                    "the label will be shown to help you choose")
    address_type = wtf.RadioField('This is a', coerce=int, default=0, validators=[wtf.Required()],
        choices = [(ADDRESSTYPE.BILLING, "Billing address"), (ADDRESSTYPE.SHIPPING, "Shipping address")])

# --- Routes: base URLs -------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='img/favicon.ico'), code=301)


# --- Routes: login/logout ----------------------------------------------------

@app.route('/login')
@lastuser.login_handler
def login():
    return {'scope': 'id email address address/new invoice'}


@app.route('/logout')
@lastuser.logout_handler
def logout():
    flash("You are now logged out", category='info')
    return request.args.get('next') or url_for('index')


@app.route('/redirect')
@lastuser.auth_handler
def lastuserauth():
    # Save the user object
    db.session.commit()
    return redirect(request.args.get('next') or url_for('index'))


@lastuser.auth_error_handler
def lastuser_error(error, error_description=None, error_uri=None):
    if error == 'access_denied':
        flash("You denied the request to login", category='error')
        return redirect(request.args.get('next') or url_for('index'))
    return render_template("autherror.html",
        error=error,
        error_description=error_description,
        error_uri=error_uri)


# --- Routes: documentation ---------------------------------------------------

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


# --- Routes: site admin ------------------------------------------------------

@app.route('/admin')
@lastuser.requires_permission('siteadmin')
def admin():
    return "Nothing here yet"


# --- Routes: account ---------------------------------------------------------

@app.route('/account')
@lastuser.requires_login
def account():
    return render_template('account.html')


@app.route('/address')
@lastuser.requires_login
def address():
    form = PostalAddressForm()
    if form.validate_on_submit():
        # Save form
        return redirect(url_for('account'))
    return render_template('autoform.html', title='Postal Address', form=form)


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
    db.create_all()
    app.run(port=4000, debug=True)
