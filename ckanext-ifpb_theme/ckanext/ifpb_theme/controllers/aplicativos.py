import ckan.plugins as p

# ============================================================
# Aplicativos
# ============================================================
class AplicativosController(p.toolkit.BaseController):
    def index (self):
		return p.toolkit.render('aplicativo/index.html')