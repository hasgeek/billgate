# -*- coding: utf-8 -*-

"""
Create and Manage Invoices
"""
from flask import g, flash, url_for, render_template, request, redirect, abort, Response
import json as simplejson
import sys
import urllib2
from werkzeug.datastructures import MultiDict
from coaster.views import load_model, load_models
from coaster import format_currency as coaster_format_currency
from baseframe.forms import render_form, render_redirect, render_delete_sqla, render_message, ConfirmDeleteForm

from billgate import app

from billgate.models import db
from billgate.models.workspace import Workspace
from billgate.models.category import Category, CATEGORY_STATUS
from billgate.models.invoice import Invoice
from billgate.models.line_item import LineItem
from billgate.views.workflows import InvoiceWorkflow

from billgate.views.login import lastuser, requires_workspace_member, requires_workspace_owner

from billgate.forms.invoice import InvoiceForm, LineItemForm


@app.template_filter('format_currency')
def format_currency(value):
    return coaster_format_currency(value, decimals=2)

def available_invoices(workspace, user=None):
    if user is None:
        user = g.user
    query = Invoice.getw(workspace)
    # FIXME+TODO: Replace with per-workspace permissions
    if 'reviewer' in lastuser.permissions():
        # Get all invoices owned by this user and in states where the user can review them
        query = query.filter(db.or_(
            Invoice.user == user, Invoice.status.in_(InvoiceWorkflow.reviewable.values)))
    else:
        query = query.filter_by(user=user)
    return query



@app.route('/<workspace>/invoices/new', methods=['GET', 'POST'])
@load_model(Workspace, {'name': 'workspace'}, 'workspace')
@requires_workspace_owner
def invoice_new(workspace):
    form = InvoiceForm(prefix='invoice')
    return invoice_edit_internal(workspace, form)

#TBD: syntax for POST?
@lastuser.resource_handler('invoice/new')
def api_invoice_new(data):
    workspace = Workspace.query.get(data.get('workspace', 'hasgeek'))
    user = User.query.get(data.get('user_id', None))
    title = data.get('title', None)
    line_items = data.get('lines', None)

    # Do we require user to be logged in? 
    if user is None:
        abort(403)

    if line_items is None:
        abort(400) 
    
    # TBD: REVIEW What is the protocol for error handling wrt missing data?
    invoice = Invoice(workspace=workspace.name, user=user)
    invoice.title = title
    invoice.make_name()
    for idx, l in enumerate(line_items):
        lineitem = LineItem()
        db.session.add(lineitem)

        lineitem.invoice_id = invoice.id
        lineitem.category_id = l.get('item_code', None)
        lineitem.description = l.get('description', None)
        lineitem.tax_rate = l.get('tax', None)
        lineitem.price_before_tax = l.get('pbt', None)
        lineitem.quantity = l.get('quantity', None)
        db.session.commit()

        lineitem.update_line_total()
        invoice.line_items.append(lineitem)
        invoice.update_total_value()
        db.session.commit()
    return jsonify(200, workspace=workspace, invoice=invoice.id, url=url_for('select_address', workspace=workspace.name, invoice=invoice.url_name))

def invoice_edit_internal(workspace, form, invoice=None, workflow=None):
    if form.validate_on_submit():
        if invoice is None:
            invoice = Invoice(workspace=workspace)
            invoice.user = g.user
        form.populate_obj(invoice)
        invoice.make_name()
        db.session.add(invoice)
        db.session.commit()
        flash("Created new invoice '%s'." % invoice.title, "success")
        return redirect(url_for('invoice', workspace=workspace.name, invoice=invoice.url_name), code=303)
    return render_template('invoice_new.html',
        workspace=workspace, form=form, invoice=invoice, workflow=workflow)



@app.route('/<workspace>/invoices/<invoice>', methods=['GET', 'POST'])
@load_models(
    (Workspace, {'name': 'workspace'}, 'workspace'),
    (Invoice, {'url_name': 'invoice', 'workspace': 'workspace'}, 'invoice')
    )
@requires_workspace_owner
def invoice(workspace, invoice):
    workflow = invoice.workflow()
    if not workflow.can_view():
        abort(403)
    lineitemform = LineItemForm()
    lineitemform.category.choices = [(c.id, c.title) for c in Category.get_by_status(workspace, CATEGORY_STATUS.LIVE)]
    lineitemform.invoice = invoice
    if lineitemform.validate_on_submit():
        if lineitemform.id.data:
            lineitem = LineItem.query.get(lineitemform.id.data)
        else:
            lineitem = LineItem()
            db.session.add(lineitem)

        lineitem.invoice_id = lineitemform.invoice.id
        lineitem.category_id = lineitemform.category.data
        category = Category.get_by_id(workspace, lineitemform.category.data).first()
        lineitem.description = category.title
        lineitem.tax_rate = category.tax_rate
        lineitem.price_before_tax = category.price_before_tax
        lineitem.quantity = lineitemform.quantity.data
        db.session.commit()
        print "1 LINE TOTAL:", lineitem.line_total
        print "INVOICE TOTAL:", invoice.total_value
        lineitem.update_line_total()
        print "2 LINE TOTAL:", lineitem.line_total
        print "INVOICE TOTAL:", invoice.total_value
        invoice.update_total_value()
        print "4 LINE TOTAL:", lineitem.line_total
        print "INVOICE TOTAL:", invoice.total_value
        db.session.commit()
        
        if request.is_xhr:
            lineitemform = LineItemForm(MultiDict())
            lineitemform.category.choices = [(c.id, c.title) for c in Category.get_by_status(workspace, CATEGORY_STATUS.LIVE)]
            return render_template("lineitem.html", workspace=workspace, invoice=invoice.url_name, lineitemform=lineitemform )
        else:
            return redirect(url_for('invoice', workspace=workspace.name, invoice=invoice.url_name, lineitemform=lineitemform, canedit=canedit), code=303)
    if request.is_xhr:
        return render_template("lineitem.html",  workspace=workspace, invoice=invoice, lineitemform=lineitemform)
    return render_template('invoice.html',
        workspace=workspace,
        invoice=invoice,
        lineitemform=lineitemform,
        workflow=workflow,
        transitions=workflow.transitions())


@app.route('/<workspace>/invoices/<invoice>/itable')
@load_models(
    (Workspace, {'name': 'workspace'}, 'workspace'),
    (Invoice, {'url_name': 'invoice', 'workspace': 'workspace'}, 'invoice')
    )
@requires_workspace_owner
def invoice_itemlisttable(workspace, invoice):
    workflow = invoice.workflow()
    if not workflow.can_view():
        abort(403)
    return render_template('itemlisttable.html', invoice=invoice, workflow=workflow)


@app.route('/<workspace>/invoices')
@load_model(Workspace, {'name': 'workspace'}, 'workspace')
@requires_workspace_member
def invoice_list(workspace):
    # Sort invoices by status
    invoices = InvoiceWorkflow.sort_documents(available_invoices(workspace).all())
    return render_template('invoices.html', invoices=invoices, invoicespage=True)


@app.route('/<workspace>/invoices/<invoice>/edit', methods=['GET', 'POST'])
@load_models(
    (Workspace, {'name': 'workspace'}, 'workspace'),
    (Invoice, {'url_name': 'invoice', 'workspace': 'workspace'}, 'invoice')
    )
@requires_workspace_member
def invoice_edit(workspace, invoice):
    workflow = invoice.workflow()
    if not workflow.can_view():
        abort(403)
    if not workflow.can_edit():
        return render_template('baseframe/message.html',
            message=u"You cannot edit this invoice at this time.")
    form = InvoiceForm(obj=invoice)
    return invoice_edit_internal(workspace, form, invoice, workflow)

    # All okay. Allow editing
    if form.validate_on_submit():
        form.populate_obj(invoice)
        db.session.commit()
        flash("Edited invoices '%s'." % invoice.title, 'success')
        return render_redirect(url_for('invoice', workspace=workspace.name, invoice=invoice.url_name), code=303)
    return render_form(form=form, title=u"Edit Invoice",
        formid="invoice_edit", submit=u"Save",
        cancel_url=url_for('invoice', workspace=workspace.name, invoice=invoice.url_name))


@app.route('/<workspace>/invoices/<invoice>/delete', methods=['GET', 'POST'])
@load_models(
    (Workspace, {'name': 'workspace'}, 'workspace'),
    (Invoice, {'url_name': 'invoice', 'workspace': 'workspace'}, 'invoice')
    )
@requires_workspace_owner
def invoice_delete(workspace, invoice):
    workflow = invoice.workflow()
    if not workflow.can_view():
        abort(403)
    if not workflow.draft():
        # Only drafts can be deleted
        return render_template('baseframe/message.html', message=u"Only draft invoices can be deleted.")
    return render_delete_sqla(invoice, db, title=u"Confirm delete",
        message=u"Delete Category '%s'?" % invoice.title,
        success=u"You have deleted '%s'." % invoice.title,
        next=url_for('invoice_list', workspace=workspace.name))


@app.route('/<workspace>/invoices/<invoice>/<line_item>/delete', methods=['GET', 'POST'])
@load_models(
    (Workspace, {'name': 'workspace'}, 'workspace'),
    (Invoice, {'url_name': 'invoice', 'workspace': 'workspace'}, 'invoice'),
    (LineItem, {'invoice': 'invoice', 'id': 'line_item'}, 'line_item')
    )
@requires_workspace_member
def line_item_delete(workspace, invoice, line_item):
    workflow = invoice.workflow()
    if not workflow.can_view():
        abort(403)
    if not workflow.can_edit():
        abort(403)
    form = ConfirmDeleteForm()
    if form.validate_on_submit():
        if 'delete' in request.form:
            db.session.delete(line_item)
            db.session.commit()
            invoice.update_total_value()
            db.session.commit()
        return redirect(url_for('invoice', workspace=workspace.name, invoice=invoice.url_name), code=303)
    return render_template('baseframe/delete.html', form=form, title=u"Confirm delete",
        message=u"Delete line item '%s' for %s %s?" % (
            line_item.category.title, invoice.currency, format_currency(line_item.line_total)))


@app.route('/<workspace>/invoices/<invoice>/submit', methods=['POST'])
@load_models(
    (Workspace, {'name': 'workspace'}, 'workspace'),
    (Invoice, {'url_name': 'invoice', 'workspace': 'workspace'}, 'invoice')
    )
@requires_workspace_member
def invoice_submit(workspace, invoice):
    wf = invoice.workflow()
    if wf.document.line_items == []:
        flash(u"This invoice does not list any line items.", 'error')
        return redirect(url_for('invoice', workspace=workspace.name, invoice=invoice.url_name), code=303)
    wf.submit()
    db.session.commit()
    flash(u"Your invoice has been submitted as Proforma Invoice.", 'success')
    return redirect(url_for('invoice', workspace=workspace.name, invoice=invoice.url_name), code=303)


@app.route('/<workspace>/invoices/<invoice>/resubmit', methods=['POST'])
@load_models(
    (Workspace, {'name': 'workspace'}, 'workspace'),
    (Invoice, {'url_name': 'invoice', 'workspace': 'workspace'}, 'invoice')
    )
@requires_workspace_member
def invoice_resubmit(workspace, invoice):
    wf = invoice.workflow()
    if wf.document.line_items == []:
        flash(u"This invoice does not list any line items.", 'error')
        return redirect(url_for('invoice', workspace=workspace.name, invoice=invoice.url_name), code=303)
    wf.resubmit()
    db.session.commit()
    flash(u"Your invoice has been re-submitted as Proforma Invoice.", 'success')
    return redirect(url_for('invoice', workspace=workspace.name, invoice=invoice.url_name), code=303)


@app.route('/<workspace>/invoices/<invoice>/accept', methods=['POST'])
@load_models(
    (Workspace, {'name': 'workspace'}, 'workspace'),
    (Invoice, {'url_name': 'invoice', 'workspace': 'workspace'}, 'invoice')
    )
@requires_workspace_member
def invoice_accept(workspace, invoice):
    wf = invoice.workflow()
    wf.accept(reviewer=g.user)
    db.session.commit()
    flash(u"Invoice '%s' has been accepted." % Invoice.title, 'success')
    return redirect(url_for('invoice_list', workspace=workspace.name), code=303)


@app.route('/<workspace>/invoice/<invoice>/return_for_review', methods=['POST'])
@load_models(
    (Workspace, {'name': 'workspace'}, 'workspace'),
    (Invoice, {'url_name': 'invoice', 'workspace': 'workspace'}, 'invoice')
    )
@requires_workspace_member
def invoice_return(workspace, invoice):
    wf = invoice.workflow()
    wf.return_for_review(reviewer=g.user, notes=u'')  # TODO: Form for notes
    db.session.commit()
    flash(u"Invoice '%s' has been returned for review." % invoice.title,
        'success')
    return redirect(url_for('invoice_list', workspace=workspace.name), code=303)


@app.route('/<workspace>/invoices/<invoice>/reject', methods=['POST'])
@load_models(
    (Workspace, {'name': 'workspace'}, 'workspace'),
    (Invoice, {'url_name': 'invoice', 'workspace': 'workspace'}, 'invoice')
    )
@requires_workspace_member
def invoice_reject(workspace, invoice):
    wf = invoice.workflow()
    wf.reject(reviewer=g.user, notes=u'')  # TODO: Form for notes
    db.session.commit()
    flash(u"Invoice '%s' has been rejected." % invoice.title, 'success')
    return redirect(url_for('invoice_list', workspace=workspace.name), code=303)


@app.route('/<workspace>/invoices/<invoice>/withdraw', methods=['POST'])
@load_models(
    (Workspace, {'name': 'workspace'}, 'workspace'),
    (Invoice, {'url_name': 'invoice', 'workspace': 'workspace'}, 'invoice')
    )
@requires_workspace_member
def invoice_withdraw(workspace, invoice):
    wf = invoice.workflow()
    wf.withdraw()
    db.session.commit()
    flash(u"Invoice '%s' has been withdrawn." % invoice.title, 'success')
    return redirect(url_for('invoice_list', workspace=workspace.name), code=303)


@app.route('/<workspace>/invoices/<invoice>/due', methods=['POST'])
@load_models(
    (Workspace, {'name': 'workspace'}, 'workspace'),
    (Invoice, {'url_name': 'invoice', 'workspace': 'workspace'}, 'invoice')
    )
@requires_workspace_member
def invoice_due(workspace, invoice):
    wf = invoice.workflow()
    wf.make_due()
    db.session.commit()
    flash(u"You have raised a formal Invoice '%s' which is now due." % invoice.title, 'success')
    return redirect(url_for('invoice_list', workspace=workspace.name), code=303)




@app.route('/<workspace>/invoices/<invoice>/paid', methods=['POST'])
@load_models(
    (Workspace, {'name': 'workspace'}, 'workspace'),
    (Invoice, {'url_name': 'invoice', 'workspace': 'workspace'}, 'invoice')
    )
@requires_workspace_member
def invoice_paid(workspace, invoice):
    wf = invoice.workflow()
    wf.due_to_paid()
    db.session.commit()
    flash(u"Invoice '%s' has been marked paid" % invoice.title, 'success')
    return redirect(url_for('invoice_list', workspace=workspace.name), code=303)



