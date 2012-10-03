from flask.ext.wtf import Form, TextField, SelectField, TextAreaField, html5
from flask.ext.wtf import Required
from billgate.models.address import countries


class AddressForm(Form):
    name = TextField('Name', validators=[Required()])
    address = TextAreaField('Address', validators=[Required()])
    city = TextField('City/District', validators=[Required()])
    state = TextField('State/Province', validators=[Required()])
    postal_code = TextField('Postal code (PIN/ZIP)', validators=[Required()])
    country = SelectField('Country', validators=[Required()], choices=countries, default="IND")
    phone = TextField("Telephone No", description="Telephone No", validators=[Required()])
    email = html5.EmailField("Email", description="Email Address, We will never spam you .",
        validators=[Required()])
