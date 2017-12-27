# encoding: utf-8

'''API functions for searching for and getting data from CKAN.'''

import uuid
import logging
import json
import datetime
import socket

from ckan.common import config
import sqlalchemy
from paste.deploy.converters import asbool

import ckan.lib.dictization
import ckan.logic as logic
import ckan.logic.action
import ckan.logic.schema
import ckan.lib.dictization.model_dictize as model_dictize
import ckan.lib.jobs as jobs
import ckan.lib.navl.dictization_functions
import ckan.model as model
import ckan.model.misc as misc
import ckan.plugins as plugins
import ckan.lib.search as search
import ckan.lib.plugins as lib_plugins
import ckan.lib.activity_streams as activity_streams
import ckan.lib.datapreview as datapreview
import ckan.authz as authz

from ckan.common import _

log = logging.getLogger('ckan.logic')

# Define some shortcuts
# Ensure they are module-private so that they don't get loaded as available
# actions in the action API.
_validate = ckan.lib.navl.dictization_functions.validate
_table_dictize = ckan.lib.dictization.table_dictize
_check_access = logic.check_access
NotFound = logic.NotFound
ValidationError = logic.ValidationError
_get_or_bust = logic.get_or_bust

_select = sqlalchemy.sql.select
_aliased = sqlalchemy.orm.aliased
_or_ = sqlalchemy.or_
_and_ = sqlalchemy.and_
_func = sqlalchemy.func
_desc = sqlalchemy.desc
_case = sqlalchemy.case
_text = sqlalchemy.text


def app_list(context, data_dict = {}):
	m = context['model']
	order_by = data_dict.get('order_by')

	query = model.Session.query(m.App)

	if order_by:
		query = query.order_by(order_by)

	lista = query.all()
	return lista

def app_show(context, data_dict = {}):
	m = context['model']
	app_id = data_dict.get('id')

	query = model.Session.query(m.App).filter_by(id = app_id)
	app = query.first()

	if app is None:
		raise NotFound(u'App não encontrado.')

	return app