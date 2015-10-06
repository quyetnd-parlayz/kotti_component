# -*- coding: utf-8 -*-

"""
Created on 2015-09-16
:author: quyetnd (quyet@parlayz.com)
"""

from zope.interface import Interface, Attribute

from zope.annotation.interfaces import IAnnotatable
from kotti_annotation.interfaces import IFlexContent


class IEntity(IFlexContent):
    """Entity as in most of component based framework
    """


class IComponent(Interface):
    """Component define a part of content of 
    """

    schema = Attribute("Schema to render form/validate input data")

    def validate(self):
        """Validate input content
        """

