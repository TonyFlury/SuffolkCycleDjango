from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.utils.html import format_html, mark_safe

import json


# ----------------------------------------------------------
#
# Maps don't get stored in the data base
#
# ----------------------------------------------------------

def confirmPropertyExists(propertyname):
    def decorator(method):
        def propertyCheck(self, *args, **kwargs):
            if propertyname not in self.__dict__:
                raise AttributeError('property {} does not exist in this {} instance'.format(
                        propertyname,
                        self.__class__.__name__))
            else:
                return method(self, *args, **kwargs)

        return propertyCheck

    return decorator


class ol2Base(object):
    __registry = {}

    def __new__(cls, *args, **kwargs):
        inst = super(ol2Base, cls).__new__(cls, *args, **kwargs)
        cls.__registry['{:016X}'.format(id(inst))] = inst
        return inst

    @classmethod
    def get_instance(cls, key):
        return cls.__registry.get(key, None)


class ol2Map(ol2Base):
    def __init__(self, **kwargs):
        """ Very simplistic Map object -
            supports JSON get functions for :
                domElement
                center
                restrictedExtent
                kmlRoute
                kmlLocations
        """
        self.__dict__.update(**kwargs)

    def get_url(self, data=None):
        return reverse('olMap2:ol2Map',
                       kwargs={'instance': '{:016X}'.format(id(self))}) + ("?data={}".format(data) if data else '')

    @confirmPropertyExists('restrictedExtent')
    def get_json_restrictedExtent(self):
        return self.__dict__['restrictedExtent']

    @confirmPropertyExists('center')
    def get_json_center(self):
        return self.__dict__['center']

    @confirmPropertyExists('kmlRoute')
    def get_json_kmlRoute(self):
        return self.__dict__['kmlRoute']

    @confirmPropertyExists('kmlLocation')
    def get_json_kmlLocation(self):
        return self.__dict__['kmlLocation']

    @confirmPropertyExists('domElement')
    def get_json_domElement(self):
        return self.__dict__['domElement']

    @confirmPropertyExists('zoom')
    def get_json_zoom(self):
        return self.__dict__['zoom']

    @confirmPropertyExists('domElement')
    def __call__(self):
        levels = lambda extent=self.__dict__.get('zoomExtent', (1,19)) : extent[1] - extent[0]
        return format_html("<div id='{domElement}' "
                           "class='ol2mapElement {classes}' "
                           "data-ol2map-instance='{instance}' "
                           "data-ol2map-center='{center}' "
                           "data-ol2map-kmlLayers='{kmlLayers}' "
                           "data-ol2map-extent='{extent}' "
                           "data-ol2map-switcher='{switcher}' "
                           "data-ol2map-zoom='{zoom}' "
                           "data-ol2map-zoomExtent='{zoomExtent}' "
                           "data-ol2map-numZoomLevel='{numZoomLevel}' "
                           ">"
                           "</div>".format(
                domElement=self.__dict__['domElement'],
                classes=("{}".format(" ".join(self.__dict__['classes']))) if 'classes' in self.__dict__ else '',
                instance=self.get_url(),
                center=json.dumps(self.__dict__.get('center', None)),
                kmlLayers=json.dumps(self.__dict__.get('kmlLayers', None)),
                extent=json.dumps(self.__dict__.get('restrictedExtent', None)),
                switcher=json.dumps(self.__dict__.get('switcher', False)),
                zoom=json.dumps(self.__dict__.get('zoom', None)),
                zoomExtent=json.dumps(self.__dict__.get('zoomExtent', (1,19))),
                numZoomLevel = json.dumps(self.__dict__.get('numZoomLevel', levels()))
        ))
