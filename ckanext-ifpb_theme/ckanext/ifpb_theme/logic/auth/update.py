# encoding: utf-8

import ckan.logic as logic
import ckan.authz as authz
import ckan.logic.auth as logic_auth

from ckan.common import _

def app_update(context, data_dict=None):
    user = context['user']
    user = authz.get_user_id_for_username(user, allow_none=True)

    if user and authz.check_config_permission('user_update_apps'):
        return {'success': True}
    return {'success': False,
            'msg': _('Usuário %s não autorizado para atualizar o app') % user}