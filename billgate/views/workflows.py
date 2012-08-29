# -*- coding: utf-8 -*-

from datetime import datetime
from flask import g
from coaster.docflow import DocumentWorkflow, WorkflowState, WorkflowStateGroup
from billgate.models.invoice import INVOICE_STATUS, Invoice
from billgate.forms.invoice import ReviewForm
from billgate.views.login import lastuser


class InvoiceWorkflow(DocumentWorkflow):
    """
    Workflow for Invoices.
    """

    state_attr = 'status'

    draft = WorkflowState(INVOICE_STATUS.DRAFT, title=u"Draft")
    proforma = WorkflowState(INVOICE_STATUS.PROFORMA, title=u"Proforma")
    review = WorkflowState(INVOICE_STATUS.REVIEW, title=u"Returned for review") # for review by seller
    accepted = WorkflowState(INVOICE_STATUS.ACCEPTED, title=u"Accepted") # by purchaser
    rejected = WorkflowState(INVOICE_STATUS.REJECTED, title=u"Rejected") # by purchaser
    withdrawn = WorkflowState(INVOICE_STATUS.WITHDRAWN, title=u"Withdrawn") # by seller
    due = WorkflowState(INVOICE_STATUS.DUE, title=u"Due")
    paid = WorkflowState(INVOICE_STATUS.PAID, title=u"Paid")

    #: States in which an owner/seller can edit
    editable = WorkflowStateGroup([draft, review], title=u"Editable")

    #: States in which a reviewer/purchaser can view
    reviewable = WorkflowStateGroup([proforma, review, accepted, rejected, due, paid],
                                    title=u"Reviewable")

    def permissions(self):
        """
        Permissions available to current user.
        """
        base_permissions = super(InvoiceWorkflow, self).permissions()
        if self.document.user == g.user:
            base_permissions.append('owner')
        base_permissions.extend(lastuser.permissions())
        return base_permissions


    @draft.transition(proforma, 'owner', title=u"Submit", category="primary",
        description=u"Submit this invoice to a reviewer? You cannot "
        "edit this invoice after it has been submitted as Proforma Invoice.",
        view='invoice_submit')
    def submit(self):
        """
        Submit the invoice as proforma.
        """
        # Update timestamp
        self.document.datetime = datetime.utcnow()
        # TODO: Notify reviewers

    @proforma.transition(due, 'owner', title=u"Raise Invoice", category="success",
        description=u"Mark this invoice as due? "
            u"This will raise a formal invoice and it cannot be edited further.",
        view='invoice_due')
    def make_due(self):
        """
        Mark this invoice as due (indicates formal invoice raised).
        """
        # Update timestamp
        self.document.datetime = datetime.utcnow()
        # TODO: Notify reviewer of due date
        pass

    @review.transition(proforma, 'owner', title=u"Submit", category="primary",
        description=u"Resubmit this invoice to a reviewer? You cannot "
        "edit this invoice after it has been submitted as Proforma Invoice.",
        view='invoice_resubmit')
    def resubmit(self):
        """
        Submit the invoice as proforma.
        """
        # Update timestamp
        self.document.datetime = datetime.utcnow()
        # TODO: Notify reviewers



    @proforma.transition(accepted, 'reviewer', title=u"Accept", category="primary",
        description=u"Accept this proforma invoice and queue it for payments?",
        view='invoice_accept')
    def accept(self, reviewer):
        """
        Accept the invoice and mark for payout to owner.
        """
        # TODO: Notify owner of acceptance
        self.document.reviewer = reviewer



    @proforma.transition(review, 'reviewer', title=u"Return for review", category="warning",
        description=u"Return this invoice to the submitter for review?",
        view='invoice_return', form=ReviewForm)
    def return_for_review(self, reviewer, notes):
        """
        Return invoice to owner for review.
        """
        # TODO: Notify owner
        self.document.reviewer = reviewer
        self.document.notes = notes


    @proforma.transition(rejected, 'reviewer', title=u"Reject", category="danger",
        description=u"Reject this invoice? Rejected invoices are archived but cannot be processed again.",
        view='invoice_reject', form=ReviewForm)
    def reject(self, reviewer, notes):
        """
        Reject invoice.
        """
        # TODO: Notify owner
        self.document.reviewer = reviewer
        self.document.notes = notes


    @review.transition(withdrawn, 'owner', title=u"Withdraw", category="danger",
        description=u"Withdraw this invoice? Withdrawn invoices are archived but cannot be processed again.",
        view='invoice_withdraw')
    def withdraw(self):
        """
        Withdraw invoice.
        """
        pass


    @accepted.transition(due, 'owner', title=u"Raise Invoice", category="success",
        description=u"Mark this invoice as due? "
            u"This will raise a formal invoice and it cannot be edited further.",
        view='invoice_due')
    def mark_due(self):
        """
        Mark invoice as due (indicates invoice raised).
        """
        # TODO: Notify reviewer who pays.
        pass


    @due.transition(paid, 'owner', title=u"Mark Paid", category="success",
        description=u"Mark this invoice as paid? "
            u"This will mark the invoice as paid, after which it will be archived.",
        view='invoice_paid')
    def due_to_paid(self):
        """
        Mark invoice as paid (indicates payment received).
        """
        # TODO: Notify reviewer who pays.
        self.document.datetime = datetime.utcnow()


    def can_view(self):
        """
        Can the current user view this?
        """
        permissions = self.permissions()
        if 'owner' in permissions:
            return True
        if 'reviewer' in permissions and self.reviewable():
            return True
        return False

    def can_edit(self):
        """
        Can the current user edit this?
        """
        return 'owner' in self.permissions() and self.editable()

# Apply this workflow on Invoice objects
InvoiceWorkflow.apply_on(Invoice)
