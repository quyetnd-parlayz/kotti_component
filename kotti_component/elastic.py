from sqlalchemy.exc import InvalidRequestError
from zope.interface import implements
from zope.component import adapts

from pyramid_es.interfaces import IElastic
from kotti_es.elastic import BaseElasticKottiContent

from kotti_component.interfaces import IEntity


class ElasticEntity(BaseElasticKottiContent):
    implements(IElastic)
    adapts(IEntity)

    def elastic_document(self):
        """
        """
        doc = super(ElasticEntity, self).elastic_document()
        doc.update(self.context.__json__())

        # TODO: Add 
        return doc
