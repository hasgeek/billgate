from billgate import app
from billgate.models import db, User
from flask import redirect, request, url_for
from flask.ext.lastuser import LastUser
from flask.ext.lastuser.mongoengine import UserManager

lastuser = LastUser(app)
user = User()
lastuser.init_usermanager(UserManager(user, User))

@app.route('/login')
@lastuser.login_handler
def login():
    return {'scope': 'id email'}


@app.route('/logout')
@lastuser.logout_handler
def logout():
    flash("You are now logged out", category='info')
    return request.args.get('next') or url_for('index')


@app.route('/login/redirect')
@lastuser.auth_handler
def lastuserauth():
    # Save the user object
    return redirect(request.args.get('next') or url_for('index'))
    
@lastuser.auth_error_handler
def lastuser_error(error, error_description=None, error_uri=None):
    if error == 'access_denied':
        flash("You denied the request to login", category='error')
        return redirect(get_next_url())
    return Response(u"Error: %s\n"
                    u"Description: %s\n"
                    u"URI: %s" % (error, error_description, error_uri),
                    mimetype="text/plain")
