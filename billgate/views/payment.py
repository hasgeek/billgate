from billgate import app
from billgate.models import Address
from billgate.views.login import lastuser
from billgate.forms import AddressForm
from flask import render_template, g, flash, redirect, url_for, request
from flask import session

@app.route('/address')
@lastuser.requires_login
def select_address(form=None):
    if form is None:
        form = AddressForm()
    context = {
        'user': g.user,
        'addresses': Address.objects(user=g.user),
        'form': form,
        'title': 'Select Billing Address',
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
        return select_address(form=form)

@app.route('/address/select/<aid>')
@lastuser.requires_login
def select_existing_address(aid):
    address = Address.objects(hashkey=aid).first()
    session['address'] = getattr(address, 'hashkey', None)
    return redirect(url_for('select_payment'))

@app.route('/address/delete/<aid>')
@lastuser.requires_login
def delete_address(aid):
    address = Address.objects(hashkey=aid).first()
    address.delete()
    if request.referrer:
        next = request.referrer
    else:
        next = url_for(index)
    return redirect()


@app.route('/address/edit/<aid>')
@lastuser.requires_login
def edit_address(aid, form=None):
    address = Address.objects(hashkey=aid).first()
    if form is None:
        form = AddressForm(obj=address)
    context = {
        'form': form,
        'title': 'Edit Address',
    }
    return render_template('edit_address.html', **context)

@app.route('/address/edit/<aid>', methods=['POST'])
@lastuser.requires_login
def process_edit_address(aid):
    address = Address.objects(hashkey=aid).first()
    form = AddressForm(obj=address)
    if form.validate_on_submit():
        address = Address()
        form.populate_obj(address)
        address.user = g.user
        address.save()
        return redirect(url_for('select_payment'))
    else:
        flash("Please check your details and try again.", 'error')
        return edit_address(address.hashkey, form=form)

@app.route('/payment')
@lastuser.requires_login
def select_payment():
    aid = session.get('address', None)
    print aid
    if aid is None:
        return redirect(url_for('select_address'))
    address = Address.objects(hashkey=aid).first()
    print address.address1
    context = {
        'user': g.user,
        'address': address,
        'title': 'Confirm Details',
    }
    return render_template('payment.html', **context)

@app.route('/response/ebs')
@lastuser.requires_login
def ebs_response():
    return redirect('/')
