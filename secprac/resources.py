from pyramid.security import Everyone, authenticated_userid

class Profile(object):
    request = None

    @property
    def __acl__(self):
        acl = [('Allow', Everyone, 'view')]
        username = authenticated_userid(self.request)

        if username == self.request.matchdict['id']:
            acl.append(('Allow', username, 'edit'))

        return acl

    def __init__(self, request):
        self.request = request

