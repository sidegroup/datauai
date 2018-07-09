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


# ============================================================
# Aplicativos
# ============================================================
class ApiController(BaseController):

	def show(self):
		return render('api/api_documentation.html')
	def developer(self):
		return render('developers/developer.html')
	def turma(self):
		return render('developers/turmas.html')
