from flask.ext.wtf import Form, TextField, IntegerField, DecimalField, SelectField, Required, NumberRange
from billgate.models.category import CATEGORY_STATUS_CODES

from billgate import app


class CategoryForm(Form):
    title = TextField('Title', validators=[Required()])
    nos_available = IntegerField("No. Available", 
    	description="The number of items available in this category in inventory", 
    	validators=[Required()])
    price_before_tax = TextField('Rate (Before Tax)', 
    	description="Unit Price before tax", validators=[Required()])
    tax_rate = DecimalField("Tax Rate (%)", places=2, 
    	description="Tax rate for this item or service category. Confirm with Government docs.", 
    	validators=[Required()])
    status = SelectField('Status', validators=[Required()], default=0,
        choices=CATEGORY_STATUS_CODES, coerce=int)