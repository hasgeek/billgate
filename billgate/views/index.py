from billgate import app
from billgate.forms import EbsForm
from flask import render_template

@app.route('/')
def index():
    context = {
        'ebsform': EbsForm(),
    }
    return render_template('index.html', **context)


@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='img/favicon.ico'), code=301)
