from flask.ext.wtf import Form, RadioField, SelectField, TextField, Required, Optional
from baseframe.forms import RichTextField
from billgate.models.workspace import CURRENCIES

__all__ = ['NewWorkspaceForm']


class NewWorkspaceForm(Form):
    """
    Create a workspace.
    """
    workspace = RadioField("Organization", validators=[Required()],
        description="Select the organization you would like to create a workspace for.")
    currency = SelectField("Currency", validators=[Required()], choices=CURRENCIES,
        description="The standard currency for your organizations accounts.")
    fullname = TextField("Fullname", validators=[Required()],
        description="Your Organization's Full Registered Name")
    address = RichTextField("Address", validators=[Required()],
        description="Your Organization's Registered Address")
    cin = TextField("Registration Number", validators=[Optional()],
        description="Your Organization's Registration Number")
    tan = TextField("TAN", validators=[Optional()],
        description="Tax Deduction Number")
    pan = TextField("PAN", validators=[Optional()],
        description="PAN Card Number")
    tin = TextField("TIN", validators=[Optional()],
        description="Tax Identification Number")