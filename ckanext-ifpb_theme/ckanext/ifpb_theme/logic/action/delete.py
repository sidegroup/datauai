# encoding: utf-8

'''API functions for deleting data from CKAN.'''

import logging

import sqlalchemy as sqla

import ckan.lib.jobs as jobs
import ckan.logic
import ckan.logic.action
import ckan.plugins as plugins
import ckan.lib.dictization.model_dictize as model_dictize
from ckan import authz

from ckan.common import _


log = logging.getLogger('ckan.logic')

validate = ckan.lib.navl.dictization_functions.validate

# Define some shortcuts
# Ensure they are module-private so that they don't get loaded as available
# actions in the action API.
ValidationError = ckan.logic.ValidationError
NotFound = ckan.logic.NotFound
_check_access = ckan.logic.check_access
_get_or_bust = ckan.logic.get_or_bust
_get_action = ckan.logic.get_action

def app_delete(context, data_dict):
    '''Delete a user.

    Only sysadmins can delete users.

    :param id: the id or usernamename of the user to delete
    :type id: string
    '''

    _check_access('app_delete', context, data_dict)

    model = context['model']
    session = context['session']
    app_id = _get_or_bust(data_dict, 'id')
    app = model.App.get(app_id)

    if app is None:
        raise NotFound('App não encontrado.')

    session.delete(app)

    session.commit()

    return app