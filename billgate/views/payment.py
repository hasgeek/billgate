from flask import g, flash, url_for, render_template, request, redirect, abort, Response
from coaster.views import load_model, load_models
from coaster.utils import format_currency as coaster_format_currency
from baseframe.forms import render_form, render_redirect, render_delete_sqla, render_message, ConfirmDeleteForm

from billgate import app
from billgate.models import db
from billgate.models import Address, Payment, PAYMENT_STATUS, Invoice, Workspace, INVOICE_STATUS
from billgate.views.login import lastuser
from billgate.forms import AddressForm
from flask import render_template, g, flash, json, redirect, url_for, request
from flask import session
from base64 import b64decode
from billgate.rc4 import crypt
from datetime import datetime


@app.route('/<workspace>/invoices/<invoice>/pay', methods=['GET', 'POST'])
@load_models(
    (Workspace, {'name': 'workspace'}, 'workspace'),
    (Invoice, {'url_name': 'invoice', 'workspace': 'workspace'}, 'invoice')
    )
@lastuser.requires_login
def select_address(invoice, workspace):
    """
    Select an Address or enter a new one. Session must contain invoice id if it exists
    """
    form = AddressForm()
    if form.validate_on_submit():
        address = Address(user=g.user)
        db.session.add(address)
        form.populate_obj(address)
        db.session.commit()
        session['workspace'] = workspace.name
        session['address'] = getattr(address, 'hashkey', None)
        session['invoice'] = invoice.id
        print "SESSION WORKSPACE:", session['workspace']
        print "SESSION ADDRESS:", session['address']
        print "SESSION INVOICE:", session['invoice']
        return redirect(url_for('confirm_payment'))
    addresses = Address.get(g.user)
    for i in invoice.lineitems:
        print "ITEM:", i.description
    return render_template('address.html.jinja2',
        form=form, invoice=invoice, workspace=workspace, addresses=addresses)


@app.route('/<workspace>/invoices/<invoice>/address/select/<aid>', methods=['GET', 'POST'])
@load_models(
    (Workspace, {'name': 'workspace'}, 'workspace'),
    (Invoice, {'url_name': 'invoice', 'workspace': 'workspace'}, 'invoice'),
    (Address, {'hashkey': 'aid'}, 'address')
    )
@lastuser.requires_login
def select_existing_address(workspace, invoice, address):
    """
    Process an existing address.
    """
    session['workspace'] = workspace.name
    session['invoice'] = invoice.id
    session['address'] = address.hashkey
    return redirect(url_for('confirm_payment'))



@app.route('/<workspace>/invoices/<invoice>/billaddress/delete/<aid>', methods=['GET', 'POST'])
@load_models(
    (Workspace, {'name': 'workspace'}, 'workspace'),
    (Invoice, {'url_name': 'invoice', 'workspace': 'workspace'}, 'invoice'),
    (Address, {'id': 'aid'}, 'address')
    )
@lastuser.requires_login
def delete_address(workspace, invoice, address):
    """
    Delete an address
    """
    return render_delete_sqla(address, db, title=u"Confirm delete",
        message=u"Delete Address '%s'?" % address.address,
        success=u"You have deleted '%s'." % address.address,
        next=url_for('select_address', workspace=workspace.name, invoice=invoice.url_name))



@app.route('/address/edit/<aid>', methods=['GET', 'POST'])
@lastuser.requires_login
def edit_address(aid):
    address = Address.query.filter_by(hashkey=aid).first()
    form = AddressForm(obj=address)
    if form.validate_on_submit():
        if address is None:
            address=Address()
            address.user = g.user
            db.session.add(address)
        form.populate_obj(address)
        db.session.commit()
        return redirect(url_for('confirm_payment'))
    return render_template('address.html.jinja2',
        user=g.user,
        addresses=Address.query.filter_by(user=g.user),
        form=form,
        title='Select Billing Address')



@app.route('/confirm')
@lastuser.requires_login
def confirm_payment():
    """
    Confirm details and make a payment.
    """
    workspace = Workspace.get(session['workspace'])
    address = Address.get_by_hashkey(session['address']).first()
    invoice = Invoice.get_by_id(workspace, session['invoice'])
    return render_template('confirm.html.jinja2', invoice=invoice, address=address, workspace=workspace, workflow=invoice.workflow())


@app.route('/response/ebs')
@lastuser.requires_login
def ebs_response():
    """
    Process response from EBS payment gateway.
    """
    data = b64decode(request.query_string[2:])
    decrypted = crypt(data, app.config['EBS_KEY'])
    response_split = {}
    status = 1
    for item in decrypted.split('&'):
        oneitem = item.split('=')
        response_split[oneitem[0]] = oneitem[1]

    #determine invoice from session
    workspace = Workspace.get(session['workspace'])
    invoice = Invoice.get_by_id(workspace, session['invoice'])
    address = Address.get_by_hashkey(session['address']).first()

    #pull out relevant info from response
    message = response_split['ResponseMessage']
    pg_transaction_id = response_split['TransactionID']
    status = response_split['ResponseCode']

    #create and save payment
    payment = Payment()
    db.session.add(payment)
    payment.invoice_id = invoice.id
    payment.response = json.dumps(response_split)
    db.session.commit()

    if status == '0':
        invoice.status = INVOICE_STATUS.PAID
    db.session.commit()

    # show transaction status
    return render_template('confirm.html.jinja2', status=status, invoice=invoice, address=address, workflow=invoice.workflow(), workspace=workspace, message=message, transaction_id=pg_transaction_id)
