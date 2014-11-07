import requests
from zipfile import ZipFile
from cStringIO import StringIO
from osgeo import ogr
import tempfile


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
            layer, 
            "query"
            )

    def get_kml(self, layer, where="1 = 1", fields="*", return_geometry=True):
        return ZipFile(StringIO(requests.get(self._build_request(layer),
            params = {
                'where': where,
                'outFields': fields,
                'returnGeometry': return_geometry,
                'f': "kmz"
            }).content), "r").open('doc.kml', 'r').read()

    def get(self, layer, where="1 = 1", fields="*", return_geometry=True):
        drv = ogr.GetDriverByName('KML')
        kml = self.get_kml(layer, where, fields, return_geometry)
        temp = tempfile.NamedTemporaryFile()
        temp.write(kml)
        temp.flush()

        datasource = drv.Open(temp.name)
        for layer in datasource:
            for feat in layer:
                print feat.ExportToJson()

        



