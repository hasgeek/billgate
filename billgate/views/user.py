from billgate import app

from flask import render_template

@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/foobar')
def address():
    form = PostalAddressForm()
    if form.validate_on_submit():
        # Save form
        return redirect(url_for('account'))
    return render_template('autoform.html', title='Postal Address', form=form)

