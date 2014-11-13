import json
import requests

class ArcGIS:
    """
    A class that can download a layer from a map in an 
    ArcGIS web service and convert it to something useful,
    like GeoJSON.

    Usage:

    >>> import arcgis
    >>> arc = arcgis.ArcGIS("http://www.pathtomapserver:6080/", "FOLDER_OF_PROJECTS", "MAP_DATA_I_WANT")
    >>> layer_id = 1
    >>> arc.get(layer_id)

    This assumes you've inspected your ArcGIS services endpoint to know what to look for.
    ArcGIS DOES publish json files enumerating the endpoints you can query, so autodiscovery
    could be possible further down the line.

    """
    def __init__(self, base_url, folder, map_name):
        self.base_url=base_url
        self.folder=folder
        self.map=map_name
        self._layer_descriptor_cache = {}
        self._geom_parsers = {
            'esriGeometryPoint': self._parse_esri_point,
            'esriGeometryMultipoint': self._parse_esri_multipoint,
            'esriGeometryPolyline': self._parse_esri_polyline,
            'esriGeometryPolygon': self._parse_esri_polygon
        }

    def _build_request(self, layer):
        return urljoin(self.base_url,
            "arcgis/rest/services", 
            self.folder,
            self.map,
            "MapServer",
            layer
            )

    def _build_query_request(self, layer):
        return urljoin(self._build_request(layer), "query")

    def _parse_esri_point(self, geom):
        return {
            "type": "Point",
            "coordinates": [
                geom.get('x'),
                geom.get('y')
            ]
        }

    def _parse_esri_multipoint(self, geom):
        return {
            "type": "MultiPoint",
            "coordinates": geom.get('points')
        }

    def _parse_esri_polyline(self, geom):
        return {
            "type": "MultiLineString",
            "coordinates": geom.get('paths')
        }    

    def _parse_esri_polygon(self, geom):
        return {
            "type": "Polygon",
            "coordinates": geom.get('rings')
        }
 
    def _determine_geom_parser(self, type):
        return self._geom_parsers.get(type)

    def esri_to_geojson(self, obj, geom_parser):
        return {
            "type": "Feature",
            "properties": obj.get('attributes'),
            "geometry": geom_parser(obj.get('geometry'))
        }

    def get_json(self, layer, where="1 = 1", fields=[], count_only=False, srid='4326'):
        """
        Gets the JSON file from ArcGIS
        """
        return requests.get(self._build_query_request(layer),
            params = {
                'where': where,
                'outFields': ", ".join(fields),
                'returnGeometry': True,
                'outSR': srid,
                'f': "pjson",
                'orderByFields': "OBJECTID",
                'returnCountOnly': count_only
            }).json()

    def get_descriptor_for_layer(self, layer):
        """
        Returns the standard JSON descriptor for the layer. There is a lot of
        usefule information in there.
        """
        if not self._layer_descriptor_cache.has_key(layer):
            response = requests.get(self._build_request(layer), params={'f': 'pjson'})
            self._layer_descriptor_cache[layer] = response.json()
        return self._layer_descriptor_cache[layer]

    def enumerate_layer_fields(self, layer):
        """
        Pulls out all of the field names for a layer.
        """
        descriptor = self.get_descriptor_for_layer(layer)
        return [field['name'] for field in descriptor['fields']]

    def get(self, layer, where="1 = 1", fields=[], count_only=False, srid='4326'):
        """
        Gets a layer and returns it as honest to God GeoJSON.

        WHERE 1 = 1 causes us to get everything. We use OBJECTID in the WHERE clause
        to paginate, so don't use OBJECTID in your WHERE clause unless you're going to 
        query under 1000 objects.
        """
        base_where = where
        print base_where
        # By default we grab all of the fields. Technically I think
        # we can just do "*" for all fields, but I found this was buggy in 
        # the KMZ mode. I'd rather be explicit. 
        fields = fields or self.enumerate_layer_fields(layer)

        jsobj = self.get_json(layer, where, fields, count_only, srid)

        # Sometimes you just want to know how far there is to go.
        if count_only:
            return jsobj.get('count')

        # From what I can tell, the entire layer tends to be of the same type,
        # so we only have to determine the parsing function once.
        geom_parser = self._determine_geom_parser(jsobj.get('geometryType'))

        features = []
        # We always want to run once, and then break out as soon as we stop
        # getting exceededTransferLimit.
        while True:
            features += [self.esri_to_geojson(feat, geom_parser) for feat in jsobj.get('features')]
            if not jsobj.get('exceededTransferLimit'):
                break
            # If we've hit the transfer limit we offset by the last OBJECTID
            # returned and keep moving along. 
            where = "OBJECTID > %s" % features[-1]['properties'].get('OBJECTID')
            if base_where != "1 = 1" :
                # If we have another WHERE filter we needed to tack that back on.
                where += " AND %s" % base_where
            print where
            jsobj = self.get_json(layer, where, fields, count_only, srid)

        return {
            'type': "FeatureCollection",
            'features': features
        }

def urljoin(*args):
    """
    There's probably a better way of handling this.
    """
    return "/".join(map(lambda x: str(x).rstrip('/'), args))
