from billgate import app

from flask import render_template

@app.route('/account')
def account():
    return render_template('account.html')


@app.route('/address')
def address():
    form = PostalAddressForm()
    if form.validate_on_submit():
        # Save form
        return redirect(url_for('account'))
    return render_template('autoform.html', title='Postal Address', form=form)

