from sqlalchemy.exc import InvalidRequestError
from zope.interface import implements
from zope.component import (
    adapts,
    )
from kotti.interfaces import (
    IContent,
    )
from pyramid_es.mixin import (
    ESMapping,
    ESString,
    ESField,
    )
from pyramid_es.elastic import ElasticBase
from pyramid_es.interfaces import IElastic
from kotti_es import ESSession
from kotti_es.util import html_to_text
from kotti_component.interfaces import IEntity


class ElasticEntity(ElasticBase):
    implements(IElastic)
    adapts(IEntity)

    def __init__(self, context):
        try:
            context.title and context.name
        except InvalidRequestError:
            self.context = ESSession.query(context.__class__).\
                filter(context.__class__.id == context.id).scalar()
            if self.context is None:
                # just in case the object was deleted
                self.context = context
        else:
            self.context = context

    def elastic_mapping(self):
        """
        This is the base fallback adapter for all contents.

        If exists an ``elastic_mapping`` configuration is available you the
        resource's ``type_info``, it will returned as it is.

        Otherwise, a very basic default mapping is returned (just ``title`` and
        ``description``).

        You can add a ``filter`` keyword argument to the ``ESString``
        properties passing a callable that accepts the value to be
        filtered/changed. For example you could pass a filter=html_to_text
        to a ``body`` property.
        """
        context = self.context
        elastic_mapping = getattr(context.type_info, 'elastic_mapping', None)
        if elastic_mapping is not None:
            return elastic_mapping
        else:
            # [TODO] To be discussed:
            # * path: enable path_hierarchy?
            # * body: do we need filtering html? ES should be able to do that
            return ESMapping(
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

    def elastic_document_type(self):
        """
        The elastic document type
        """
        return self.context.type_info.name

    def elastic_document_id(self):
        """
        The elastic document id
        """
        return self.context.id

    # Attr private methods
    @property
    def _id(self):
        return self.elastic_document_id()

    @property
    def _title(self):
        return self.context.title

    @property
    def _description(self):
        return self.context.description

    @property
    def _body(self):
        body = getattr(self.context, 'body', '')
        return body

    @property
    def _path(self):
        return self.context.path

    @property
    def _name(self):
        return self.context.name

    @property
    def _language(self):
        return self.context.language

    @property
    def _state(self):
        return self.context.state