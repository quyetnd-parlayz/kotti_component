# -*- coding: utf-8 -*-

import colander
from pydoc import locate
from zope.interface import implements

from sqlalchemy.orm import relation
from sqlalchemy.orm import backref
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Boolean
from sqlalchemy import Text
from sqlalchemy import String
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.ext.associationproxy import association_proxy

from kotti import Base
from kotti.interfaces import IDefaultWorkflow
from kotti.resources import Content
from kotti.sqla import NestedMutationList
from kotti.sqla import NestedMutationDict
from kotti.sqla import JsonType

from kotti_annotation.sqla import JSONAlchemy
from zope.annotation.interfaces import IAnnotations
from kotti_component.interfaces import IEntity
from kotti_component import _


def cls_lookup(self, klass):
    if '.' not in klass:
        klass = 'colander.' + klass
    return locate(klass)


class SchemaValidator(Base):
    """Define a Validator of a schema node 
    """

    schemanode_id = Column(Integer, ForeignKey('schema_nodes.id'), primary_key=True)
    klass = Column(String(50))
    args = Column(NestedMutationList.as_mutable(JsonType))
    kwargs = Column(NestedMutationDict.as_mutable(JsonType))
    position = Column(Integer())

    parent = relation(
        'SchemaNode',
        backref=backref(
            '_validators',
            collection_class=ordering_list('position'),
            order_by=[position],
            cascade='all',
        )
    )

    def cook(self):
        """Return a validator object
        """
        return cls_lookup(self.klass)(*self.args, **self.kwargs)


class SchemaNode(Base):
    """SchemaNode is a Schema
    """

    __tablename__ = 'schema_nodes'

    #: Primary key for the node in the DB
    #: (:class:`sqlalchemy.types.Integer`)
    id = Column(Integer(), primary_key=True)
    #: Schemanode is children of Dataschema
    #: (:class:`sqlalchemy.types.String`)
    component_id = Column(Integer, ForeignKey('components.id'))
    #: Name of the node
    #: (:class:`sqlalchemy.types.String`)
    name = Column(String(50))
    #: Value type of the node, use to lookup the SchemaNode class to instantiate
    #: (:class:`sqlalchemy.types.String`)
    klass = Column(String(50))
    #: Annotation value
    #: (:class:`kotti.sqla.JsonType`)
    default = Column(JSONAlchemy(Text))
    #: 
    #: 
    required = Column(Boolean)
    #: Position of the node within its container / parent
    #: (:class:`sqlalchemy.types.Integer`)
    position = Column(Integer())
    #: Additional arguments like title, description, widget name etc
    kwargs = Column(NestedMutationDict.as_mutable(JsonType))

    parent = relation(
        'Component',
        backref=backref(
            '_schemanodes',
            collection_class=ordering_list('position'),
            order_by=[position],
            cascade='all',
        )
    )

    def cook(self):
        """Return colander's schemanode object from the 
        """
        # ATM only "all" composition are supported
        validators = [ v.cook()
            for v in self._validators
            ]
        if len(validators) == 0:
            validator = None
        elif len(validators) == 1:
            validator = validators[0]
        else:
            validator = colander.all(*validators)
        return colander.SchemaNode(
            name=self.name,
            typ=cls_lookup(self.klass),
            default=self.default,
            missing=self.required and colander.required or colander.drop,
            validator=validator,
            )


class Component(Content):
    """Component define a part of Entity. 
       An Entity can add/remove a Component dynamically. 
       TypeInfo hold information about how the Component be structured
    """

    id = Column(Integer, ForeignKey('contents.id'), primary_key=True)

    def schema(self):
        """Build colander schema from associated schema nodes
        """
        schema = colander.SchemaNode(colander.Mapping())
        for node in self._schemanodes:
            schema.add(node.cook())

    def save(self, entity, cstruct):
        """Save data to the entity instance
        """
        schema = self.schema()
        appstruct = schema.deserialize(cstruct)
        for key in appstruct:
            entity.key = appstruct[key]
        # if self not in entity.components:
        #     entity.components.append(self)
        #TODO: Fire event ?

    def load(self, entity):
        """Load enity to display friendly 
        """
        appstruct = {}
        for node in self._schemanodes:
            appstruct[node.name] = getattr(entity, name)
        return schema.serialize(appstruct)

    def reindex(self):
        """Reindex the component
        """

    def search(self, query):
        """Search within the component
        """

    def __json__(self):
        """
        """
        return dict((key, getattr(key) for key in 
            self.__table__.columns.keys() + self._annotations.keys()))


class ComponentToEntity(Base):
    """Schema to Component Typeinfo mapping
    """

    __tablename__ = 'components_to_entities'

    #: Foreign key referencing :attr:`Component.id`
    #: (:class:`sqlalchemy.types.Integer`)
    component_id = Column(Integer, ForeignKey('components.id'), primary_key=True)
    #: Foreign key referencing :attr:`Entity.id`
    #: (:class:`sqlalchemy.types.Integer`)
    entity_id = Column(Integer, ForeignKey('entities.id'), primary_key=True)
    #: Ordering position
    #: :class:`sqlalchemy.types.Integer`
    position = Column(Integer, nullable=False)
    #: Relation that adds a ``content_tags`` :func:`sqlalchemy.orm.backref`
    #: to :class:`~kotti.resources.Tag` instances to allow easy access to all
    #: content tagged with that tag.
    #: (:func:`sqlalchemy.orm.relationship`)
    entity = relation(
        "Entity", 
        backref=backref('_components', 
            collection_class=ordering_list('position'),
            order_by=[position],
            cascade='all, delete-orphan')
        )
    component = relation(Component)


class Entity(Content):
    """Entity mimics behaviour of Plone dexterity's Item and reddit's Thing
       with ability to set/get foreign attributes via Annotation Storage
    """

    __tablename__ = 'entities'
    implements(IEntity)

    id = Column(Integer(), ForeignKey('contents.id'), primary_key=True)
    components = association_proxy('_components', 'component')

    type_info = Content.type_info.copy(
        name=u'Entity',
        title=_(u'Entity'),
        add_view=u'add_entity',
        addable_to=[u'Entity', u'Document'],
        )

    base_mapping = ESMapping(
        analyzer='content',
        properties=ESMapping(
            ESField('_id'),
            ESString('title', attr='_title'),
            ESString('description', attr='_description'),
            ESString('body', attr='_body', filter=html_to_text),
            ESField('path',
                    attr='_path',
                    index='not_analyzed',
                    ),
            ESField('name',
                    attr='_name',
                    index='not_analyzed',
                    ),
            ESField('language',
                    attr='_language',
                    index='not_analyzed',
                    ),
            ESField('state',
                    attr='_state',
                    index='not_analyzed',
                    ),
            ))

    def __init__(self, **kwargs):
        super(Entity, self).__init__(**kwargs)

    def __setattr__(self, name, value):
        if not hasattr(self, name) and not name.startswith('_'):
            IAnnotations(self)[name] = value
        else:
            super(Entity, self).__setattr__(name,value)

    def __getattr__(self, name):
        try:
            return super(Entity, self).__getattr__(name)
        except AttributeError:
            if name.startswith('_'):
                raise AttributeError
            anno = IAnnotations(self)
            if name in anno:
                return anno[name]
            raise AttributeError


class I18nAttribute(Base):
    """SchemaNode is a Schema
    """

    __tablename__ = 'i18n'

    #: Foreign key referencing :attr:`Node.id`
    #: (:class:`sqlalchemy.types.Integer`)
    node_id = Column(Integer, ForeignKey('nodes.id'), primary_key=True)
    #: Name of the attribute
    #: (:class:`sqlalchemy.types.String`)
    name = Column(String(50), primary_key=True)
    #: Language of the translatetion
    #: (:class:`kotti.sqla.JsonType`)
    lang = Column(String(10))
    #: Translation value
    #: (:class:`kotti.sqla.JsonType`)
    value = Column(JSONAlchemy(Text))
    node = relation(Node, backref=backref(
            "_i18n", 
            collection_class=attribute_mapped_collection('name'),
            cascade="all, delete-orphan"
            )
        )

    def __repr__(self): # pragma: no cover
        return str("%s:%s" % (str(getattr(self.node, self.name)), str(self.value)))
        # return u"<Annotation '{0}' of '{1}': {2}>".format(
        #     self.name, self.node.__repr__(), self.value)

    def __init__(self, node_id, name, lang, value):
        self.node_id = node_id
        self.name = name
        self.lang = lang
        self.value = value

