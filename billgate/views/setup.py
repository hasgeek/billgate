# -*- coding: utf-8 -*-

"""
Setup Workspace, Create and Manage Items
"""

from flask import flash, url_for, render_template, g
from coaster.views import load_model, load_models
from baseframe.forms import render_form, render_redirect, render_delete_sqla, render_message

from billgate import app
from billgate.models import db
from billgate.views.login import lastuser, requires_workspace_member, requires_workspace_owner

from billgate.models.category import Category
from billgate.models.workspace import Workspace

from billgate.forms.category import CategoryForm
from billgate.forms.workspace import NewWorkspaceForm, CURRENCIES


@app.route('/new', methods=['GET', 'POST'])
@lastuser.requires_login
def workspace_new():
    # Step 1: Get a list of organizations this user owns
    existing = Workspace.query.filter(Workspace.userid.in_(g.user.organizations_owned_ids())).all()
    existing_ids = [e.userid for e in existing]
    # Step 2: Prune list to organizations without a workspace
    new_workspaces = []
    for org in g.user.organizations_owned():
        if org['userid'] not in existing_ids:
            new_workspaces.append((org['userid'], org['title']))
    if not new_workspaces:
        return render_message(
            title=u"No organizations remaining",
            message=u"You do not have any organizations that do not yet have a workspace.")

    # Step 3: Ask user to select organization
    form = NewWorkspaceForm()
    form.workspace.choices = new_workspaces
    if form.validate_on_submit():
        # Step 4: Make a workspace
        org = [org for org in g.user.organizations_owned() if org['userid'] == form.workspace.data][0]
        workspace = Workspace(name=org['name'], title=org['title'], userid=org['userid'],
            currency=form.currency.data, fullname=form.fullname.data, address=form.address.data,
            cin=form.cin.data,pan=form.pan.data,tin=form.tin.data,tan=form.tan.data)
        db.session.add(workspace)
        db.session.commit()
        flash("Created new workspace for %s" % workspace.title, "success")
        return render_redirect(url_for('workspace_view', workspace=workspace.name), code=303)
    return render_form(form=form, title="Create a new organization workspace", submit="Create",
        formid="workspace_new", cancel_url=url_for('index'), ajax=False)

@app.route('/<workspace>/edit', methods=['GET', 'POST'])
@load_model(Workspace, {'name': 'workspace'}, 'workspace')
@requires_workspace_owner
def workspace_edit(workspace):
    form = NewWorkspaceForm()
    form.currency.choices = CURRENCIES
    if form.validate_on_submit():
        form.populate_obj(workspace)
        db.session.add(workspace)
        db.session.commit()
        flash("Saved workspace %s" % workspace.title, "success")
        return render_redirect(url_for('workspace_view', workspace=workspace.name), code=303)
    return render_form(form=form, title="Edit organization workspace", submit="Save",
        formid="workspace_edit", cancel_url=url_for('workspace_view', workspace=workspace.name), ajax=False)


@app.route('/<workspace>/')
@load_model(Workspace, {'name': 'workspace'}, 'workspace')
@requires_workspace_member
def workspace_view(workspace):
    return render_template('workspace.html', workspace=workspace)


@app.route('/<workspace>/categories/')
@load_model(Workspace, {'name': 'workspace'}, 'workspace')
@requires_workspace_member
def category_list(workspace):
    categories = Category.get(workspace)
    return render_template('categories.html', categories=categories)
    


@app.route('/<workspace>/categories/new', methods=['GET', 'POST'])
@load_model(Workspace, {'name': 'workspace'}, 'workspace')
@requires_workspace_owner
def category_new(workspace):
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(workspace=workspace)
        form.populate_obj(category)
        category.make_name()
        db.session.add(category)
        db.session.commit()
        flash("Created new category in workspace '%s'." % workspace.name, "success")
        return render_redirect(url_for('category_list', workspace=workspace.name), code=303)
    return render_form(form=form, title=u"Create new category",
        formid="category_new", submit=u"Create",
        cancel_url=url_for('category_list', workspace=workspace.name), ajax=False)


@app.route('/<workspace>/categories/<category>/edit', methods=['GET', 'POST'])
@load_models(
    (Workspace, {'name': 'workspace'}, 'workspace'),
    (Category, {'name': 'category', 'workspace': 'workspace'}, 'category')
    )
@requires_workspace_owner
def category_edit(workspace, category):
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        form.populate_obj(category)
        category.make_name()
        db.session.commit()
        flash("Edited item '%s'" % category.name, "success")
        return render_redirect(url_for('category_list', workspace=workspace.name), code=303)
    return render_form(form=form, title=u"Edit Category",
        formid='category_edit', submit=u"Save",
        cancel_url=url_for('category_list', workspace=workspace.name), ajax=True)

@app.route('/<workspace>/categories/<category>')
@load_models(
    (Workspace, {'name': 'workspace'}, 'workspace'),
    (Category, {'name': 'category', 'workspace': 'workspace'}, 'category')
    )
@requires_workspace_member
def category(workspace, category):
    return render_template('category.html', category=category)

@app.route('/<workspace>/categories/<category>/delete', methods=['GET', 'POST'])
@load_models(
    (Workspace, {'name': 'workspace'}, 'workspace'),
    (Category, {'name': 'category', 'workspace': 'workspace'}, 'category')
    )
@requires_workspace_owner
def category_delete(workspace, category):
    return render_delete_sqla(category, db, title=u"Confirm delete",
        message=u"Delete Category '%s'?" % category.title,
        success=u"You have deleted category '%s'." % category.title,
        next=url_for('category_list', workspace=workspace.name))

