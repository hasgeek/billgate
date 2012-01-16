from billgate import app
from flask import render_template, redirect, url_for

@app.route('/')
def index():
    context = {
    }
    return render_template('index.html', **context)


@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='img/favicon.ico'), code=301)
