# encoding: utf-8

import logging
import datetime
import time
import json
import mimetypes

from ckan.common import config
import paste.deploy.converters as converters

import ckan.lib.helpers as h
import ckan.plugins as plugins
import ckan.logic as logic
import ckan.lib.dictization.model_dictize as model_dictize
import ckan.lib.dictization.model_save as model_save
import ckan.lib.navl.dictization_functions
import ckan.lib.navl.validators as validators
import ckan.lib.plugins as lib_plugins
import ckan.lib.email_notifications as email_notifications
import ckan.lib.search as search
import ckan.lib.uploader as uploader
import ckan.lib.datapreview
import ckan.lib.app_globals as app_globals
import ckan.lib.dictization as d


from ckan.common import _, request

log = logging.getLogger(__name__)

# Define some shortcuts
# Ensure they are module-private so that they don't get loaded as available
# actions in the action API.
_validate = ckan.lib.navl.dictization_functions.validate
_get_action = logic.get_action
_check_access = logic.check_access
NotFound = logic.NotFound
ValidationError = logic.ValidationError
_get_or_bust = logic.get_or_bust

def app_update(context, data_dict):
    model = context['model']
    user = context['user']
    session = context['session']
    schema = context.get('schema')
    id = _get_or_bust(data_dict, 'id')

    _check_access('app_update', context, data_dict)

    app_obj = model.App.get(id)
    context['app_obj'] = app_obj
    if app_obj is None:
        raise NotFound('App não encontrado.')


    data, errors = _validate(data_dict, schema, context)
    if errors:
        session.rollback()
        raise ValidationError(errors)

    app_obj.name = data_dict.get('name')
    app_obj.description = data_dict.get('description')
    app_obj.image_url = data_dict.get('image_url')

    app = d.table_dictize(app_obj, context)

    session.commit()

    log.debug('Atualizado app {name}'.format(name=app_obj.name))
    return data_dict