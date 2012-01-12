from billgate import app
from billgate.models import Address
from billgate.views.login import lastuser
from billgate.forms import AddressForm
from flask import render_template, g, flash, redirect, url_for, session

@app.route('/address')
@lastuser.requires_login
def select_address():
    context = {
        'user': g.user,
        'addresses': Address.objects(user=g.user),
        'form': AddressForm(),
    }
    return render_template('address.html', **context)

@app.route('/address', methods=['POST'])
@lastuser.requires_login
def process_select_address():
    form = AddressForm()
    if form.validate_on_submit():
        address = Address()
        form.populate_obj(address)
        address.user = g.user
        address.save()
        session['address'] = address.hashkey
        return redirect(url_for('select_payment'))
    else:
        flash("Please check your details and try again.", 'error')
        return select_address(eventname, regform=form)

@app.route('/address/select/<aid>')
@lastuser.requires_login
def select_existing_address(aid):
    address = Address.objects(hashkey=aid).first()
    session['address'] = getattr(address, hashkey, None)
    return redirect(url_for('select_payment'))

@app.route('/payment')
@lastuser.requires_login
def select_payment():
    context = {
        'user': g.user,
        'address': Address.objects(hashkey=session['address']).first(),
    }
    return render_template('payment.html', **context)
