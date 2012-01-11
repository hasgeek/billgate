from flaskext.wtf import (
    Form,
    TextField,
    SelectField,
    Required,
    RadioField,
    Email,
    )
from billgate import app

class EbsForm(Form):
    name = TextField('Your name', validators=[Required()])
    address = TextField('Address', validators=[Required()])
    address2 = TextField('Address')
    address3 = TextField('Address')
    city = TextField('City/District', validators=[Required()])
    state = TextField('State/Province', validators=[Required()])
    postal_code = TextField('Postal code (PIN/ZIP)', validators=[Required()])
    country = SelectField('Country', validators=[Required()], default='IND',
        choices=app.config.get('COUNTRY_LIST', []))
    phone = TextField('Phone', validators=[Required()],
        description="The telephone number associated with this address")
    label = TextField('Label',
        description="Give this address an optional label. If you have multiple addresses, "
                    "the label will be shown to help you choose")
