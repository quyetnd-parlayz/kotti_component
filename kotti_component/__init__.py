# -*- coding: utf-8 -*-

"""
Created on 2015-09-28
:author: quyetnd (quyet@parlayz.com)
"""

from kotti.resources import Document
from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('kotti_component')


def kotti_configure(settings):
    """ Add a line like this to you .ini file::

            kotti.configurators =
                kotti_component.kotti_configure

        to enable the ``kotti_component`` add-on.

    :param settings: Kotti configuration dictionary.
    :type settings: dict
    """

    settings['pyramid.includes'] += ' kotti_component'
    settings['kotti.available_types'] += ' kotti_component.resources.Entity'
    Document.type_info.addable_to.append('Entity')


def includeme(config):
    """ Don't add this to your ``pyramid_includes``, but add the
    ``kotti_configure`` above to your ``kotti.configurators`` instead.

    :param config: Pyramid configurator object.
    :type config: :class:`pyramid.config.Configurator`
    """

    config.include('pyramid_zcml')
    config.load_zcml('configure.zcml')
    
    config.scan(__name__)
