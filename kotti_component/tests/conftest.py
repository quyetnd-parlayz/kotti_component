# -*- coding: utf-8 -*-

pytest_plugins = "kotti"

from pytest import fixture


@fixture(scope='session')
def custom_settings():
    import kotti_component.resources
    kotti_component.resources  # make pyflakes happy
    return {
        'kotti.configurators': 'kotti_annotation.kotti_configure '
                               'kotti_component.kotti_configure'}
