from flaskext.wtf import (
    Form,
    TextField,
    SelectField,
    Required,
    RadioField,
    Email,
    )
from billgate import app

class AddressForm(Form):
    name = TextField('Your name', validators=[Required()])
    address1 = TextField('Address', validators=[Required()])
    address2 = TextField('Address', validators=[Required()])
    city = TextField('City/District', validators=[Required()])
    state = TextField('State/Province', validators=[Required()])
    postal_code = TextField('Postal code (PIN/ZIP)', validators=[Required()])
    country = SelectField('Country', validators=[Required()], default='IND',
        choices=app.config.get('COUNTRY_LIST', []))
    phone = TextField('Phone', validators=[Required()],
        description="The telephone number associated with this address")
