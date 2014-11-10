import json
import requests
from zipfile import ZipFile
from cStringIO import StringIO
from osgeo import ogr
import tempfile
from BeautifulSoup import BeautifulSoup


def urljoin(*args):
    """
    Kinda ghetto.
    """
    return "/".join(map(lambda x: str(x).rstrip('/'), args))

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

    def get_kml(self, layer, where="1 = 1", fields=[], return_geometry=True):
        """
        Gets the KMZ file from ArcGIS, unzips it in memory and returns the 
        contents of the KML file inside.
        """
        return ZipFile(StringIO(requests.get(self._build_query_request(layer),
            params = {
                'where': where,
                'outFields': ", ".join(fields),
                'returnGeometry': return_geometry,
                'f': "kmz"
            }).content), "r").open('doc.kml', 'r').read()

    def _table_to_properties(self, obj):
        """
        Takes the HTML description table in the JSON and 
        parses it into a real object we can replace the 
        HTML-infested version with.
        """
        html = obj.get("properties").get("Description")
        soup = BeautifulSoup(html)
        # For some reason there's a nested table, and that has the info.
        tds = map(lambda x: x.getText(), soup.findAll("table")[1].findAll("td"))
        ret = {}
        # Split up the tds into pairs and zip em together as dicts.
        for pair in zip(tds[::2], tds[1::2]):
            ret.update({pair[0]: pair[1]})
        return ret

    def get_descriptor_for_layer(self, layer):
        return requests.get(self._build_request(layer), params={'f': 'pjson'}).json()

    def enumerate_layer_fields(self, layer):
        descriptor = self.get_descriptor_for_layer(layer)
        return [field['name'] for field in descriptor['fields']]

    def get(self, layer, where="1 = 1", fields=[], return_geometry=True):
        """
        Gets a layer and returns it as honest to God GeoJSON.

        We take their KML and do some transformations to make it useful.
        """

        # By default we grab all of the layer fields 
        fields = fields or self.enumerate_layer_fields(layer)

        drv = ogr.GetDriverByName('KML')
        kml = self.get_kml(layer, where, fields, return_geometry)
        temp = tempfile.NamedTemporaryFile()
        temp.write(kml)
        temp.flush()

        datasource = drv.Open(temp.name)
        features = []
        for layer in datasource:
            for feat in layer:
                jsobj = json.loads(feat.ExportToJson())
                jsobj["properties"] = self._table_to_properties(jsobj)
                features.append(jsobj)

        return {
            'type': "FeatureCollection",
            'features': features
        }