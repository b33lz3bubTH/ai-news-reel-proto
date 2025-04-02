from src.resources.entities.controllers import router as entities_router
from src.resources.tenants.controllers import router as tenants_router
from src.resources.socials.controllers import router as socials_router

routes = [tenants_router, entities_router, socials_router]
