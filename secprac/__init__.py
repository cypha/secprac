from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Everyone, Allow
from secprac.resources import Profile

from .models import DBSession, User

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')

    authn_policy = AuthTktAuthenticationPolicy(secret='s0secret')
    authz_policy = ACLAuthorizationPolicy()

    DBSession.configure(bind=engine)
    config = Configurator(settings=settings, root_factory='secprac.RootFactory')
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('register', '/register')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('update_profile', '/update_profile')

    config.add_route('profile', '/{username}', factory=Profile)
    config.scan()
    return config.make_wsgi_app()

class RootFactory(object):
    __acl__ = [
        (Allow, Everyone, 'view'),
    ]

    def __init__(self, request):
        pass

