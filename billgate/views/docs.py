from billgate import app
from flask import render_template


@app.route('/privacy')
def privacy():
    return render_template('privacy.html', title="Privacy Policy")


@app.route('/terms')
def terms():
    return render_template('terms.html', title="Terms & Conditions")


@app.route('/refunds')
def refunds():
    return render_template('refunds.html', title="Cancellation & Refund Policy")


@app.route('/disclaimer')
def disclaimer():
    return render_template('disclaimer.html', title="Disclaimer")
