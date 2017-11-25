import ckan.lib.helpers as h

def count_organizations():
	organizations = h.organizations_available('create_dataset')
	count = len(organizations)
	return count