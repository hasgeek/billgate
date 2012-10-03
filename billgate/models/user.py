# -*- coding: utf-8 -*-

from flask.ext.lastuser.sqlalchemy import UserBase
from billgate.models import db

__all__ = ['User', 'PROFILE_TYPE']


class PROFILE_TYPE:
    UNDEFINED = 0
    PERSON = 1
    ORGANIZATION = 2
    EVENTSERIES = 3


class User(UserBase, db.Model):
    __tablename__ = 'user'
