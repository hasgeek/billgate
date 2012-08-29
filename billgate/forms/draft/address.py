from flask.ext.wtf import Form, TextField, SelectField
from flask.ext.wtf import Required, Email, Length, URL, ValidationError
from flask.ext.wtf.html5 import EmailField
from baseframe.staticdata import country_codes
from billgate import app

class AddressForm(Form):
    name = TextField('Name', validators=[Required()])
    address1 = TextField('Address 1', validators=[Required()])
    address2 = TextField('Address 2', validators=[Required()])
    city = TextField('City/District', validators=[Required()])
    state = TextField('State/Province', validators=[Required()])
    postal_code = TextField('Postal code (PIN/ZIP)', validators=[Required()])
    country = SelectField('Country', validators=[Required()], choices=country_codes, default='INR')
    #phone = TextField('Phone', validators=[Required()], description="The telephone number associated with this address")



    