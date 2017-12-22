# -*- coding: utf-8 -*-

import ckan.plugins as p
import ckan.logic as logic
import ckan.lib.captcha as captcha
import ckan.lib.helpers as h
import ckan.lib.navl.dictization_functions as dictization_functions

from ckanext.ifpb_theme import model as ifpb_model

from ckan.lib.base import model, render, abort, BaseController
from ckan.common import _, c, request, response

from ckan.lib.navl.validators import (ignore_missing,
                                      keep_extras,
                                      not_empty,
                                      empty,
                                      ignore,
                                      if_empty_same_as,
                                      not_missing,
                                      ignore_empty
                                      )


get_action = logic.get_action
unflatten = dictization_functions.unflatten

check_access = logic.check_access
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
DataError = dictization_functions.DataError

def app_schema():
	schema = {
		'id': [ignore_missing, unicode],
		'name': [not_empty, unicode],
		'description': [ignore_missing, unicode],
		'image_url': [ignore_missing, unicode],
		'created': [ignore]
    }
	return schema

# ============================================================
# Aplicativos
# ============================================================
class AppController(BaseController):
	
	def show(self):
		context = {'model': ifpb_model}
		data_dict = {'order_by': 'name'}
		lista = get_action('app_list')(context, data_dict)
		return render('app/index.html', extra_vars={'lista': lista})

	def new(self, data=None, errors=None, error_summary=None):
		context = {'model': ifpb_model,
                   'session': model.Session,
                   'user': c.user,
                   'auth_user_obj': c.userobj,
                   'schema': app_schema(),
                   'save': 'save' in request.params}

		try:
			check_access('app_create', context)
		except NotAuthorized:
			abort(403, _('Sem autorização para criar um app'))

		if context['save'] and not data:
			return self._save_new(context)
		
		data = data or {}
		errors = errors or {}
		error_summary = error_summary or {}
		vars = {'data': data, 'errors': errors, 'error_summary': error_summary}
		
		return render('app/new.html')

	def _save_new(self, context):
		try:
			data_dict = logic.clean_dict(unflatten(logic.tuplize_dict(logic.parse_params(request.params))))
			context['message'] = data_dict.get('log_message', '')
			captcha.check_recaptcha(request)
			app = get_action('app_create')(context, data_dict)
		except NotAuthorized:
			abort(403, _('Sem autorização para criar um app'))
		except NotFound, e:
			abort(404, _('App não encontrado'))
		except DataError:
			abort(400, _(u'Error de integridade'))
		except captcha.CaptchaError:
			error_msg = _(u'Bad Captcha. Please try again.')
			h.flash_error(error_msg)
			return self.new(data_dict)
		except ValidationError, e:
			errors = e.error_dict
			error_summary = e.error_summary
			return self.new(data_dict, errors, error_summary)

		h.flash_success(_('App "%s" cadastrado com sucesso') %
                            (data_dict['name']))

		h.redirect_to('/apps')