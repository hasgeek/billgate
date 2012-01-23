from billgate import app
from billgate.models import Address, Payment, Invoice
from billgate.views.login import lastuser
from billgate.forms import AddressForm
from flask import render_template, g, flash, json, redirect, url_for, request
from flask import session
from base64 import b64decode
from billgate.rc4 import crypt
from datetime import datetime


@app.route('/address/<ino>')
@lastuser.requires_login
def select_address(ino=None, form=None):
    """
    Select an Address or enter a new one.
    """
    if form is None:
        form = AddressForm()
    if ino is None:
        return redirect(url_for('index'))
    invoice = Invoice.objects(id=ino).first()
    if invoice is None:
        return redirect(url_for('index'))
    session['invoice'] = invoice.id
    context = {
        'user': g.user,
        'addresses': Address.objects(user=g.user),
        'form': form,
        'title': 'Select Billing Address',
    }
    return render_template('address.html', **context)

@app.route('/address/<ino>', methods=['POST'])
@lastuser.requires_login
def process_select_address(ino=None):
    """
    Process a new address.
    """
    form = AddressForm()
    if form.validate_on_submit():
        #TODO: Do something empty invoice
        invoice = Invoice.objects(id=ino).first()
        #TODO: Do something about no invoice matching this id
        #Save the address first
        address = Address()
        form.populate_obj(address)
        address.user = g.user
        address.save()
        #Save the address details into the invoice
        for suffix in ['address1', 'address2', 'city', 'state', 'country']:
            setattr(invoice, ''.join(['billing_', suffix]), getattr(address,
                suffix))
            setattr(invoice, ''.join(['shipping_', suffix]), getattr(address,
                suffix))
        invoice.name = address.name
        invoice.telephone = address.phone
        invoice.save()
        return redirect(url_for('select_payment'))
    else:
        flash("Please check your details and try again.", 'error')
        return select_address(form=form)

@app.route('/address/select/<aid>')
@lastuser.requires_login
def select_existing_address(aid):
    """
    Process an existing address.
    """
    address = Address.objects(hashkey=aid).first()
    session['address'] = getattr(address, 'hashkey', None)
    ino = session['invoice']
    # Do something about empty invoice number
    invoice = Invoice.objects(id=ino).first()
    # Do something about empty invoice
    #Save the address details into the invoice
    for suffix in ['address1', 'address2', 'city', 'state', 'country',
    'postal_code']:
        setattr(invoice, ''.join(['billing_', suffix]), getattr(address,
            suffix))
        setattr(invoice, ''.join(['shipping_', suffix]), getattr(address,
            suffix))
    invoice.name = address.name
    invoice.telephone = address.phone
    invoice.save()
    return redirect(url_for('select_payment'))

@app.route('/address/delete/<aid>')
@lastuser.requires_login
def delete_address(aid):
    """
    Delete an address
    """
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
    """
    Edit an existing address
    """
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
    """
    Confirm details and make a payment.
    """
    ino = session.get('invoice', None)
    if ino is None:
        return redirect(url_for('select_address'))
    invoice = Invoice.objects(id=ino).first()
    context = {
        'user': g.user,
        'invoice': invoice,
        'title': 'Confirm Details',
    }
    return render_template('payment.html', **context)

@app.route('/response/ebs')
@lastuser.requires_login
def ebs_response():
    """
    Process response from EBS payment gateway.
    """
    data = b64decode(request.query_string[2:])
    decrypted = crypt(data, app.config['EBS_KEY'])
    response_split = {}
    for item in decrypted.split('&'):
        oneitem = item.split('=')
        response_split[oneitem[0]] = oneitem[1]
    pay = Payment()
    pay.response = response_split
    pay.save()
    context = {
        'data': data,
        'response': response_split,
    }
    return render_template('thanks.html', **context)

@app.route('/invoice/create', methods=['POST'])
@lastuser.requires_login
def create_invoice():
    data = json.loads(request.form['data'])
    total = 0
    print data['data']
    for item in data['data']:
        total += item['cost'] * item['quantity']
    invoice = Invoice(lineitems=data['data'],
                      amount=total,
                      date=datetime.now())
    invoice.save()
    return str(url_for('pay_invoice', ino=invoice.id, _external=True))

@app.route('/invoice/pay/<ino>', )
@lastuser.requires_login
def pay_invoice(ino = None):
    if ino is None:
        return url_for(index)
    invoice = Invoice.objects(id=ino).first()
    #TODO: BIG HACK AND SECURITY BUG. Needs to be removed as soon as lastuser stuff is ready
    invoice.user = g.user
    invoice.save()
    if invoice is None:
        return url_for(index)
    context = {
        'invoice': invoice,
        'user': g.user,
    }
    return render_template('pay_invoice.html', **context)
