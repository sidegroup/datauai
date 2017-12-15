import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

# Custom helper
from ckanext.ifpb_theme import helpers as h


class Ifpb_ThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IRoutes)

    def update_config(self, config_):
    	toolkit.add_template_directory(config_, 'templates')
    	toolkit.add_public_directory(config_, 'public')
    	toolkit.add_resource('fanstatic', 'ifpb_theme')

	# Registro dos helpers
    # =======================================================
    def get_helpers(self):
        '''Register all functions
        '''
        
        # Template helper function names should begin with the name of the
        # extension they belong to, to avoid clashing with functions from
        # other extensions.
        return {
            # Homepage
            'count_organizations': h.organization.count_organizations
        }

    # Mapeamento das URLs
    # =======================================================                
    def before_map(self, map):
        return map

    def after_map(self, map):
        # App
        map.connect('app', '/aplicativos',
                    controller='ckanext.ifpb_theme.controllers.aplicativos:AplicativosController',
                    action='index')
                    
        return map
