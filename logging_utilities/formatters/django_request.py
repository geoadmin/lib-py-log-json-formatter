import json

from django.http import HttpRequest


def request_to_json(request):
    return {'request': str(request)}


class DjangoJsonEncoder(json.JSONEncoder):

    def default(self, obj):  # pylint: disable=arguments-differ
        if isinstance(obj, HttpRequest):
            return request_to_json(obj)
        return json.JSONEncoder.default(self, obj)
