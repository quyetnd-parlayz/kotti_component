# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults

from kotti.util import title_to_name

from kotti_component.interfaces import IEntity
from kotti_component.resources import Entity


@view_defaults(renderer='json', name="xxx")
class EntityCRUDView(object):

    def __init__(self, context, request):

        self.context = context
        self.request = request

    # @view_config(request_method="POST", permission='add')
    @view_config(request_method="POST")
    def post(self):
        # import pdb; pdb.set_trace()
        cstruct = self.request.json
        if 'name' in cstruct:
            name = cstruct['name']
        else:
            title = cstruct.get('title', None)
            if not title:
                self.request.response.status = 400
                return {'error': "Object construction require either 'name' or 'title'"}
            name = title_to_name(title)

        #TODO: Check name occopuied or not
        #TODO: Component validation

        obj = Entity(name=name)
        for key in cstruct:
            setattr(obj, key, cstruct[key])
        self.context[name] = obj
        self.request.response.status = 201
        return {}

    @view_config(request_method="GET", permission='view')
    def get(self):
        return self.context.__json__()

    @view_config(request_method="DELETE", permission='delete')
    def delete(self):
        del self.parent[self.name]
        return {}

    @view_config(request_method="PUT", permission='edit')
    def put(self):
        cstruct = self.request.json

    @view_config(request_method="PATCH", permission='edit')
    def patch(self):
        cstruct = self.request.json
        #TODO: Component validation
        self.update(cstruct)
        return self.__json__

    @view_config(name="upload", request_method="POST", permission="add")
    def upload(self):
        pass