# encoding: utf-8

import datetime

from sqlalchemy import orm, types, Column, Table, ForeignKey, or_, and_
import vdm.sqlalchemy

import ckan.model.meta as meta
import ckan.model.core as core
import ckan.model.types as _types
import ckan.model.domain_object as domain_object

app_table = Table('app', meta.metadata,
                    Column('id', types.UnicodeText,
                           primary_key=True,
                           default=_types.make_uuid),
                    Column('name', types.UnicodeText),
                    Column('description', types.UnicodeText),
                    Column('image_url', types.UnicodeText),
                    Column('app_url', types.UnicodeText),
                    Column('created', types.DateTime,
                           default=datetime.datetime.now))

vdm.sqlalchemy.make_table_stateful(app_table)


class App(vdm.sqlalchemy.StatefulObjectMixin,
            domain_object.DomainObject):

    def __init__(self, name=u'', description=u'', image_url=u''):
        self.name = name
        self.description = description
        self.image_url = image_url

    @property
    def display_name(self):
        return self.name

    @classmethod
    def get(cls, reference):
        '''Returns a app object referenced by its id or name.'''
        query = meta.Session.query(cls).filter(cls.id == reference)
        app = query.first()
        return app

    @classmethod
    def all(cls):
        """
        Returns all apps.
        """
        q = meta.Session.query(cls)

        return q.all()


meta.mapper(App, app_table)