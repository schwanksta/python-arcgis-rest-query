import json
import unittest
from arcgis import ArcGIS

class ArcGISTest(unittest.TestCase):
    """
    Make sure we didn't break stuff
    """
    def test_count(self):
        states = ArcGIS("http://tigerweb.geo.census.gov/arcgis/rest/services/Basemaps/CommunityTIGER/MapServer")
        count = states.get(28, count_only=True)
        self.assertEqual(count, 56)
        count = states.get(28, where="NAME = 'Florida'", count_only=True)
        # Only one Florida.
        self.assertEqual(count, 1)

    def test_features(self):
        districts = ArcGIS("http://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/USA_Congressional_Districts/FeatureServer")
        features = districts.get(0, "STATE_ABBR = 'IN'")
        # Make sure we have all of the actual congressional
        # district shapes for Indiana.
        self.assertEqual(len(features.get('features')), 9)
        # Make sure they're polygons
        self.assertEqual(features.get('features')[0].get('geometry').get('type'), "Polygon")
        # Make sure it's valid json when we dump it 
        self.assertTrue(features == json.loads(json.dumps(features)))
        # Make sure a value that should be there is ther.
        self.assertEqual(features.get('features')[0].get('properties').get('STATE_ABBR'), 'IN')

    def test_field_filter(self):
        districts = ArcGIS("http://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/USA_Congressional_Districts/FeatureServer")
        # How many fields are there in the layer?
        num_fields = districts.enumerate_layer_fields(0)
        self.assertEqual(len(num_fields), 12)
        # We should only have one property, OBJECTID.
        features = districts.get(0, where="STATE_ABBR = 'IN'", fields=['OBJECTID'])
        self.assertEqual(len(features.get('features')[0].get('properties')), 1)

    def test_multiple(self):
        districts = ArcGIS("http://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Legislative/MapServer")
        # Gets 114th and 113th congressional districts for hawaii.
        features = districts.getMultiple([0, 12], where="STATE = 15")
        self.assertEqual(len(features.get('features')), 4)
        


if __name__ == '__main__':
    unittest.main()
