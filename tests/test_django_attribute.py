import unittest
import logging
from logging import Formatter
import sys
from collections import OrderedDict
import json

from django.conf import settings
from django.test import RequestFactory

from logging_utilities.filters.django_attribute import FlattenDjangoRequest
from logging_utilities.filters.django_attribute import JsonDjangoRequest
from logging_utilities.formatters.json_formatter import JsonFormatter

# From python3.7, dict is ordered
if sys.version_info >= (3, 7):
    dictionary = dict
else:
    dictionary = OrderedDict

settings.configure()


class RecordDjangoAttributesTest(unittest.TestCase):

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    @classmethod
    def _configure_django_filter(
        cls, logger, flatten=False, jsonify=False, include_keys=None, exclude_keys=None
    ):
        logger.setLevel(logging.DEBUG)

        for handler in logger.handlers:

            if flatten:
                django_filter = FlattenDjangoRequest()
                handler.addFilter(django_filter)
                handler.setFormatter(
                    Formatter("%(levelname)s:%(message)s:%(request_method)s:%(request_path)s")
                )
            elif jsonify:
                django_filter = JsonDjangoRequest(
                    include_keys=include_keys, exclude_keys=exclude_keys
                )
                handler.addFilter(django_filter)
                formatter = JsonFormatter(
                    dictionary([
                        ('level', 'levelname'),
                        ('message', 'message'),
                        ('request', 'request'),
                    ]),
                    remove_empty=True
                )
                handler.setFormatter(formatter)
            else:
                handler.setFormatter(Formatter("%(levelname)s:%(message)s:%(request)s"))

    # def test_django_request_flatten(self):
    #     request = self.factory.get('/my_path?test=true&test_2=false')
    #     with self.assertLogs('test_formatter', level=logging.DEBUG) as ctx:
    #         logger = logging.getLogger('test_formatter')
    #         self._configure_django_filter(logger, flatten=True)
    #         logger.info('Simple message', extra={'request': request})
    #         logger.info(
    #             'Composed message: %s', 'this is a composed message', extra={'request': request}
    #         )
    #     self.assertEqual(
    #         ctx.output,
    #         [
    #             "INFO:Simple message:GET:/my_path",
    #             "INFO:Composed message: this is a composed message:GET:/my_path",
    #         ]
    #     )

    def test_django_include_keys(self):
        # pylint: disable=protected-access
        django_filter = JsonDjangoRequest(
            include_keys=[
                'request.META.METHOD',
                'request.environ',
                'request.environ._include',
            ]
        )
        # True assertions
        self.assertTrue(django_filter._include_key('request', 'request'))
        self.assertTrue(django_filter._include_key('request.META', 'META'))
        self.assertTrue(django_filter._include_key('request.META.METHOD', 'METHOD'))
        self.assertTrue(django_filter._include_key('request.environ', 'environ'))
        self.assertTrue(django_filter._include_key('request.environ.CONTENT_TYPE', 'CONTENT_TYPE'))
        self.assertTrue(django_filter._include_key('request.environ._include', '_include'))
        # False assertions
        self.assertFalse(django_filter._include_key('test', 'test'))
        self.assertFalse(django_filter._include_key('request.path', 'path'))
        self.assertFalse(django_filter._include_key('request.path.full', 'full'))
        self.assertFalse(django_filter._include_key('request.META.CONTENT_TYPE', 'CONTENT_TYPE'))
        self.assertFalse(django_filter._include_key('request.META.extend.TYPE', 'TYPE'))
        self.assertFalse(django_filter._include_key('request.environ._type', '_type'))

    def test_django_exclude_keys(self):
        # pylint: disable=protected-access
        django_filter = JsonDjangoRequest(exclude_keys=['request.META.METHOD', 'request.environ'])
        # True assertions
        self.assertTrue(django_filter._exclude_key('request.META.METHOD', 'METHOD'))
        self.assertTrue(django_filter._exclude_key('request.environ', 'environ'))
        self.assertTrue(django_filter._exclude_key('request.environ.CONTENT_TYPE', 'CONTENT_TYPE'))
        self.assertTrue(django_filter._exclude_key('request.environ._include', '_include'))
        self.assertTrue(django_filter._exclude_key('request.environ._type', '_type'))
        # False assertions
        self.assertFalse(django_filter._exclude_key('test', 'test'))
        self.assertFalse(django_filter._exclude_key('request.path', 'path'))
        self.assertFalse(django_filter._exclude_key('request.path.full', 'full'))
        self.assertFalse(django_filter._exclude_key('request.META.CONTENT_TYPE', 'CONTENT_TYPE'))
        self.assertFalse(django_filter._exclude_key('request.META.extend.TYPE', 'TYPE'))
        self.assertFalse(django_filter._exclude_key('request', 'request'))
        self.assertFalse(django_filter._exclude_key('request.META', 'META'))

    def test_django_request_jsonify(self):
        request = self.factory.get('/my_path?test=true&test_2=false')
        with self.assertLogs('test_formatter', level=logging.DEBUG) as ctx:
            logger = logging.getLogger('test_formatter')
            self._configure_django_filter(
                logger,
                jsonify=True,
                include_keys=[
                    'request.META.REQUEST_METHOD', 'request.META.SERVER_NAME', 'request.environ'
                ],
                exclude_keys=['request.META.SERVER_NAME', 'request.environ.wsgi']
            )
            logger.info('Simple message', extra={'request': request})
            logger.info(
                'Composed message: %s', 'this is a composed message', extra={'request': request}
            )
        self.assertEqual(
            ctx.output,
            [
                json.dumps({
                    "level": "INFO",
                    "message": "Simple message",
                    "request": {
                        "environ": {
                            "HTTP_COOKIE": "",
                            "PATH_INFO": "/my_path",
                            "REMOTE_ADDR": "127.0.0.1",
                            "REQUEST_METHOD": "GET",
                            "SCRIPT_NAME": "",
                            "SERVER_NAME": "testserver",
                            "SERVER_PORT": "80",
                            "SERVER_PROTOCOL": "HTTP/1.1",
                            "QUERY_STRING": "test=true&test_2=false"
                        },
                        "META": {
                            "REQUEST_METHOD": "GET"
                        }
                    }
                }),
                json.dumps({
                    "level": "INFO",
                    "message": "Composed message: this is a composed message",
                    "request": {
                        "environ": {
                            "HTTP_COOKIE": "",
                            "PATH_INFO": "/my_path",
                            "REMOTE_ADDR": "127.0.0.1",
                            "REQUEST_METHOD": "GET",
                            "SCRIPT_NAME": "",
                            "SERVER_NAME": "testserver",
                            "SERVER_PORT": "80",
                            "SERVER_PROTOCOL": "HTTP/1.1",
                            "QUERY_STRING": "test=true&test_2=false"
                        },
                        "META": {
                            "REQUEST_METHOD": "GET"
                        }
                    }
                }),
            ]
        )
