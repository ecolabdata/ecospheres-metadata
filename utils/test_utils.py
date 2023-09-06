import unittest
from utils.utils import (
    get_environment_tag,
    get_value_from_json_serialization,
    get_value_from_xml,
    date_string_to_datetime
)
import re


class TestUtiles(unittest.TestCase):
    def test_get_environment_tag(self):
        host = "edmock-preprod-ecosql-pg.test-pre3.mock.fr"
        database = "ckan"

        tag = get_environment_tag(host, database)
        self.assertTrue(
            re.search("^[0-9]{8}-[0-9]{6}_%s_%s" % (host, database), tag) is not None
        )

    def test_get_value_from_json_serialization(self):
        # Read URIs
        data = '[{"uri": "http://www.opengis.net/def/crs/EPSG/0/2154"}, {"uri": "http://www.opengis.net/def/crs/EPSG/0/2972"}]'
        uri_values = get_value_from_json_serialization(data, key="uri")
        self.assertListEqual(
            uri_values,
            [
                "http://www.opengis.net/def/crs/EPSG/0/2154",
                "http://www.opengis.net/def/crs/EPSG/0/2972",
            ],
        )

        # Empty data case
        data = None
        uri_values = get_value_from_json_serialization(data, key="uri")
        self.assertListEqual(uri_values, [])

    def test_get_value_from_xml(self):
        uri = "http://www.opengis.net/def/crs/EPSG/0/4463"
        tag = "gml:identifier"
        attributes = {"codespace": "EPSG"}
        result = get_value_from_xml(uri, tag, **attributes)
        self.assertListEqual(["4463"], result)

        uri = "http://www.opengis.net/def/crs/EPSG/0/440"
        result = get_value_from_xml(uri, tag, **attributes)
        self.assertListEqual([], result)
        
    def test_date_string_to_datetime(self):
        date = "2019-06-27"
        date_as_datetime = date_string_to_datetime(date)
        self.assertEqual(2019, date_as_datetime.year)
        self.assertEqual(6, date_as_datetime.month)
        self.assertEqual(27, date_as_datetime.day)
        
        # Invalid isoformat
        date = "27-06-2019"
        self.assertIsNone(date_string_to_datetime(date))
        
    
if __name__ == "__main__":
    unittest.main(verbosity=3)
