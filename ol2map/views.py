"""
ol2map views
"""

from django.http.response import JsonResponse, HttpResponseBadRequest

import models


def json_get(request, instance):
    """Get json data"""
    data = request.GET.get('data', '')
    map = models.ol2Map.get_instance(instance)

    if not isinstance(map, models.ol2Map) or data == '':
        return HttpResponseBadRequest()

    try:
        return JsonResponse(getattr(map, 'get_json_{}'.format(data))(),safe=False)
    except AttributeError:
        print "Attribute Error"
        return JsonResponse(None, safe=False)