from pyramid.view import view_config
from pyramid.security import remember, forget, authenticated_userid, unauthenticated_userid, has_permission
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
import pdb

from .models import (
    DBSession,
    User,
    )

@view_config(route_name='home', renderer='templates/index.jinja2')
def my_view(request):
    users = DBSession.query(User).all()
    msg = 'Hi, here is auth test'
    return {'msg':msg, 'users':users}

@view_config(route_name='register', renderer='templates/register.jinja2')
def register(request):
    if request.POST:
        location = request.route_url('home')
        name = request.POST['name']
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password != confirm_password:
            return Response('Passwords do not match')

        user = User(
            name=name,
            username=username,
            password=password,
        )

        DBSession.add(user)
        try:
            DBSession.flush()
        except IntegrityError as e:
            for field in object_mapper(user).iterate_properties:
                ## make sure not a RelationshipProperty, or any other
                if (field.key in e.message) and\
                 (isinstance(field, ColumnProperty)):
                    print field.key, getattr(user, field.key)
                    e.field = {field.key : getattr(user, field.key)}
            raise e

        headers = remember(request, username)
        request.response.headerlist.extend(headers)
        return HTTPFound(location=location, headers=headers)
    return {}

@view_config(route_name='login')
def login(request):
    location = request.route_url('home')
    username = request.POST['username']
    password = request.POST['password']
    if User.check_password(username, password):
        headers = remember(request, username)
        return HTTPFound(location=location, headers=headers)
    else:
        return Response('wrong username/password')

@view_config(route_name='logout')
def logout(request):
    location = request.route_url('home')
    headers = forget(request)
    return HTTPFound(location=location, headers=headers)

@view_config(route_name='profile', renderer='templates/profile.jinja2')
def profile(request):
    username = request.matchdict['username']
    try:
        profile_data = DBSession.query(User).filter(User.username==username).first()
    except Exception as e:
        return Response('no such user')
    if has_permission('edit', request.context, request):
        return {'profile_data':profile_data, 'authenticated_userid':authenticated_userid(request)}
    else:
        {'profile_data':profile_data}
    

@view_config(route_name='update_profile', request_method='POST')
def update_profile(request):
    came_from = request.POST['came_from']
    about_me = request.POST['about_me']
    user_id=(DBSession.query(User).filter(User.username==authenticated_userid(request)).first()).id
    user = User(
        id=user_id,
        about_me=about_me
    )
    
    DBSession.merge(user)
    try:
        DBSession.flush()
    except IntegrityError as e:
        for field in object_mapper(user).iterate_properties:
            ## make sure not a RelationshipProperty, or any other
            if (field.key in e.message) and\
             (isinstance(field, ColumnProperty)):
                print field.key, getattr(user, field.key)
                e.field = {field.key : getattr(user, field.key)}
        raise e

    return HTTPFound(location=came_from)
