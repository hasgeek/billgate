from pytz import utc, timezone
from flask import render_template, g
from coaster.views import load_model
from billgate import app
from flask import render_template, redirect, url_for

from billgate.models.category import Category
from billgate.models.workspace import Workspace
from billgate.views.workflows import InvoiceWorkflow
from billgate.views.login import lastuser, requires_workspace_member


@app.context_processor
def sidebarvars():
    if hasattr(g, 'user'):
        # More access control?
        org_ids = g.user.organizations_memberof_ids()
    else:
        org_ids = []
    workspaces = Workspace.query.filter(Workspace.userid.in_(org_ids)).order_by('title').all()
    if hasattr(g, 'workspace'):
        return {
            'workspaces': workspaces,
            'categories': Category.get(g.workspace).order_by('title').all(),
            'invoice_states': InvoiceWorkflow.states(),
            'permissions': lastuser.permissions()
        }
    else:
        return {
            'workspaces': workspaces,
        }


@app.route('/')
def index():
    context = {
    }
    return render_template('index.html', **context)


@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='img/favicon.ico'), code=301)


@app.template_filter('shortdate')
def shortdate(date):
    tz = timezone(app.config['TIMEZONE'])
    return utc.localize(date).astimezone(tz).strftime('%b %e')


@app.template_filter('longdate')
def longdate(date):
    tz = timezone(app.config['TIMEZONE'])
    return utc.localize(date).astimezone(tz).strftime('%B %e, %Y')
