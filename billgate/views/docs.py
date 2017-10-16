from billgate import app
from flask import render_template


@app.route('/privacy')
def privacy():
    return render_template('privacy.html.jinja2', title="Privacy Policy")


@app.route('/terms')
def terms():
    return render_template('terms.html.jinja2', title="Terms & Conditions")


@app.route('/refunds')
def refunds():
    return render_template('refunds.html.jinja2', title="Cancellation & Refund Policy")


@app.route('/disclaimer')
def disclaimer():
    return render_template('disclaimer.html.jinja2', title="Disclaimer")
