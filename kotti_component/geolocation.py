from colander import Invalid
from colander import null

from deform.widget import Widget


class GeoPoint(object):
    """ Base class for geolocation type
    """
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon


class GeoPointType(object):
    """ Colander type definition for geopoint
    """

    def serialize(self, node, appstruct):
        if appstruct is null:
            return null
        if not isinstance(appstruct, bool):
            raise Invalid(node, '%r is not a boolean' % appstruct)
        return appstruct and 'true' or 'false'

    def deserialize(self, node, cstruct):
        if cstruct is null:
            return null
        if isinstance(cstruct, basestring):
            # "lat,lon", geohash not supported (yet)
            try:
                lat,lon = [float(s) for s in cstruct.split(",",1)]
            except:
                raise Invalid(node, '%r must in "%f,%f" format' %r)
        if isinstance(cstruct, list):
            # (lon, lat). Order for geojson spec
            if len(cstruct) != 2 :
                raise Invalid(node, "%r must be a pair of floats." %cstruct)
            lon, lat = cstruct
        if isinstance(cstruct, dict):
            # {"lat": lat, "lon": lon}
            if "lat" not in cstruct or "lon" not in cstruct:
                raise Invalid(node, '%r must have "lat" and "lon" keys' %cstruct)
            lat = cstruct["lat"]
            lon = cstruct["lon"]
        if not isinstance(lat, float) or isinstance(lon, float):
            raise Invalid(node, "%r's lat and lon must be float")
        return GeoPoint(lat, lon)

    def cstruct_children(self, node, cstruct):
        return []


class GeoPointWidget(Widget):
    """GeoPoint widget."""
    template = 'geopoint'
    readonly_template = 'readonly/geopoint'
    type_name = 'date'
    requirements = ( ('jquery', None), ('jquery_locationpicker', None))

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = ''
        readonly = kw.get('readonly', self.readonly)
        template = readonly and self.readonly_template or self.template
        options = dict(
            kw.get('options') or self.options or self.default_options
            )
        options['submitFormat'] = 'yyyy-mm-dd'
        kw.setdefault('options_json', json.dumps(options))
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        if pstruct in ('', null):
            return null
        return pstruct
