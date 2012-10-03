from decimal import Decimal
from billgate.models import db, BaseScopedIdNameMixin
from billgate.models.workspace import Workspace

__all__ = ['Category', 'CATEGORY_STATUS']


class CATEGORY_STATUS:
    DRAFT = 1
    LIVE = 2
    EXPIRED = 3

CATEGORY_STATUS_CODES = [
    [1, "Draft"],
    [2, "Live"],
    [3, "Expired"]
]


class Category(BaseScopedIdNameMixin, db.Model):
    """
    Categories are classes of items that can be purchased, along with inventory available, unit price and tax rate
    Categories can be in Draft, Live or Expired state.
    """
    __tablename__ = 'category'

    workspace_id = db.Column(db.Integer, db.ForeignKey('workspace.id'), nullable=False)
    workspace = db.relation(Workspace, backref=db.backref('Categories', cascade='all, delete-orphan'))
    parent = db.synonym('workspace')

    nos_available = db.Column(db.Integer, default=0, nullable=False)
    pat = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.0'))
    tax_rate = db.Column(db.Numeric(2, 2), nullable=False, default=Decimal('0.0'))

    status = db.Column(db.Integer, default=CATEGORY_STATUS.DRAFT, nullable=False)

    __table_args__ = (db.UniqueConstraint('name', 'workspace_id'),)

    @classmethod
    def get(cls, workspace):
        return cls.query.filter_by(workspace=workspace)

    @classmethod
    def get_by_id(cls, workspace, id):
        return cls.query.filter_by(workspace=workspace, id=id)

    @classmethod
    def get_by_status(cls, workspace, status):
        return cls.query.filter_by(workspace=workspace, status=status)
