from coffin import shortcuts
from django.template import RequestContext
from django.http import HttpResponse
from django.core import serializers
from django import http
import settings
import json

def render_json(request, data):
    response = json.dumps(data)
    return HttpResponse(response, mimetype='application/json')

def render_to_string(request, template, context):
    if request:
        context_instance = RequestContext(request)
    else:
        context_instance = None
    return shortcuts.render_to_string(template, context, context_instance)

def render_to_response(request,template, context={}, mimetype="text/html"):
    context['user'] = request.user if hasattr(request,'user') else None
    context['url'] = lambda url:settings.URL_ROOT+url
    response = render_to_string(request,template, context)
    return HttpResponse(response, mimetype=mimetype)

class Jinja2ResponseMixin(object):
    def render_to_response(self,context):
        return shortcuts.render_to_string(self.template_name, context)

class JSONResponseMixin(object):
    def render_to_response(self, context):
        "Returns a JSON response containing 'context' as payload"
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        return http.HttpResponse(content,
                                 content_type='application/json',
                                 **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return json.dumps(context)
