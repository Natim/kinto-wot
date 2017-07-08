import unittest
import webtest

import kinto.core
from pyramid.config import Configurator

from kinto_wot import __version__ as plugin_version


def get_request_class(prefix):

    class PrefixedRequestClass(webtest.app.TestRequest):

        @classmethod
        def blank(cls, path, *args, **kwargs):
            path = '/%s%s' % (prefix, path)
            return webtest.app.TestRequest.blank(path, *args, **kwargs)

    return PrefixedRequestClass


class BaseWebTest(object):
    """Base Web Test to test your cornice service.

    It setups the database before each test and delete it after.
    """

    api_prefix = "v0"

    def __init__(self, *args, **kwargs):
        super(BaseWebTest, self).__init__(*args, **kwargs)
        self.app = self._get_test_app()
        self.headers = {
            'Content-Type': 'application/json',
        }

    def _get_test_app(self, settings=None):
        config = self._get_app_config(settings)
        wsgi_app = config.make_wsgi_app()
        app = webtest.TestApp(wsgi_app)
        app.RequestClass = get_request_class(self.api_prefix)
        return app

    def _get_app_config(self, settings=None):
        config = Configurator(settings=self.get_app_settings(settings))
        kinto.core.initialize(config, version='0.0.1')
        return config

    def get_app_settings(self, additional_settings=None):
        settings = {**kinto.core.DEFAULT_SETTINGS}
        settings['includes'] = 'kinto_wot'

        if additional_settings is not None:
            settings.update(additional_settings)
        return settings


class CapabilityTestView(BaseWebTest, unittest.TestCase):

    def test_wot_capability(self, additional_settings=None):
        resp = self.app.get('/')
        capabilities = resp.json['capabilities']
        self.assertIn('wot', capabilities)
        expected = {
            "version": plugin_version,
            "url": "https://github.com/Natim/kinto-wot",
            "description": "Handle WoT action URL."
        }
        self.assertEqual(expected, capabilities['wot'])
