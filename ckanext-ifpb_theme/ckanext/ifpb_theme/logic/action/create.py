import logging
import mimetypes
import random
import re
from socket import error as socket_error

import paste.deploy.converters
from sqlalchemy import func

import ckan.lib.plugins as lib_plugins
import ckan.logic as logic
import ckan.plugins as plugins
import ckan.lib.dictization
import ckan.logic.action
import ckan.logic.schema
import ckan.lib.dictization.model_dictize as model_dictize
import ckan.lib.dictization.model_save as model_save
import ckan.lib.navl.dictization_functions
import ckan.lib.uploader as uploader
import ckan.lib.navl.validators as validators
import ckan.lib.mailer as mailer
import ckan.lib.datapreview
import ckan.lib.dictization as d

from ckan.common import _, config

# FIXME this looks nasty and should be shared better
from ckan.logic.action.update import _update_package_relationship

log = logging.getLogger(__name__)

# Define some shortcuts
# Ensure they are module-private so that they don't get loaded as available
# actions in the action API.
_validate = ckan.lib.navl.dictization_functions.validate
_check_access = logic.check_access
_get_action = logic.get_action
ValidationError = logic.ValidationError
NotFound = logic.NotFound
_get_or_bust = logic.get_or_bust

def app_create(context, data_dict):
    '''
        Create a new app.

    '''
    model = context['model']
    schema = context.get('schema')
    session = context['session']

    _check_access('app_create', context, data_dict)

    data, errors = _validate(data_dict, schema, context)

    if errors:
        session.rollback()
        raise ValidationError(errors)

    App = model.App

    app = d.table_dict_save(data_dict, App, context)

    session.commit()

    log.debug('Criado app {name}'.format(name=app.name))
    return data_dict