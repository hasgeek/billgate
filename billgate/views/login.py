from billgate import app
from billgate.models import db, User


@app.route('/login')
def login():
    return {'scope': 'id email'}


@app.route('/logout')
def logout():
    flash("You are now logged out", category='info')
    return request.args.get('next') or url_for('index')


@app.route('/redirect')
def lastuserauth():
    # Save the user object
    db.session.commit()
    return redirect(request.args.get('next') or url_for('index'))
