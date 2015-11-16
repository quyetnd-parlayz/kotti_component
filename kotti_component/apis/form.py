# -*- coding: utf-8 -*-

import colander
from kotti.views.edit import ContentSchema
from kotti.views.form import AddFormView
from kotti.views.form import EditFormView
from pyramid.view import view_config

from kotti_component import _
from kotti_component.resources import Entity


@view_config(name=Entity.type_info.add_view, 
             permission=Entity.type_info.add_permission,
             renderer='kotti:templates/edit/node.pt')
class EntityAddForm(AddFormView):
    """ Form to add a new instance of Entity. """

    def schema_factory(self):
        return self.context.cook()

    add = Entity
    item_type = _(u"Entity")


@view_config(name='edit', context=Entity, permission='edit',
             renderer='kotti:templates/edit/node.pt')
class EntityEditForm(EditFormView):
    """ Form to edit existing Entity objects. """

    def schema_factory(self):
        return self.context.cook()

