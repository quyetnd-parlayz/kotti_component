# -*- coding: utf-8 -*-

from pytest import raises


class TestResource:

    def test_model(self, config, root, db_session):
        from kotti_component.resources import Entity
        from zope.annotation.interfaces import IAnnotations

        config.include('kotti_annotation')
        config.include('kotti_component')

        cc = Entity()

        # Test annotation
        cc.aa = u'Foo'
        assert 'aa' in IAnnotations(cc)
        assert IAnnotations(cc)['aa'] == u'Foo'

        with raises(AttributeError):
            cc.bb
