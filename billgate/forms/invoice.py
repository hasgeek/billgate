from decimal import Decimal
from flask import g

from baseframe.forms import RichTextField
from flask_wtf import Form, TextField, SelectField, IntegerField, ValidationError, Required, Optional

from billgate.models.lineitem import LineItem
from billgate.models.workspace import CURRENCIES

__all__ = ['InvoiceForm', 'LineItemForm', 'WorkflowForm', 'ReviewForm']


class InvoiceForm(Form):
    """
    Create an Invoice
    """
    title = TextField(u"Title", validators=[Required()],
        description=u"What is this invoice for?")
    addressee = TextField(u"Addressed To", validators=[Required()],
        description=u"Person/Organization this invoice is addressed to")
    description = RichTextField(u"Description", validators=[Optional()],
        description=u"Notes on the Invoice. Add payment terms here.")
    currency = SelectField(u"Currency", validators=[Required()],
        description=u"Currency for items in this invoice",
        choices=CURRENCIES, default='INR')


class LineItemForm(Form):
    """
    Create or edit a line item.
    """
    id = IntegerField(u"Id", validators=[Optional()])
    category = SelectField(u"Category", validators=[Required()], coerce=int)
    quantity = IntegerField(u"Quantity", validators=[Required()])

    def validate_id(self, field):
        # Check if user is authorized to edit this line item
        if field.data:
            lineitem = LineItem.query.get(field.data)
            if not lineitem:
                raise ValidationError("Unknown line item")
            if lineitem.invoice.workspace != g.user.workspace:
                raise ValidationError("You are not authorized to edit this line item")

    def validate_quantity(self, field):
        if field.data < Decimal('0.01'):
            raise ValidationError("Quantity should be more than zero")


class WorkflowForm(Form):
    """
    Blank form for CSRF in workflow submissions.
    """
    pass


class ReviewForm(Form):
    """
    Reviewer notes on invoices.
    """
    notes = RichTextField(u"Notes", validators=[Required()])
