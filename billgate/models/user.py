# -*- coding: utf-8 -*-

from flask import url_for
from flask.ext.lastuser.sqlalchemy import UserBase
from billgate.models import db

__all__ = ['User']


class User(UserBase, db.Model):
    __tablename__ = 'user'
