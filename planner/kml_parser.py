import xml.etree.ElementTree as ET

class KMLParser:
    @staticmethod
    def parse_kml(file_path):
        """
        Parse the KML and return a dict with:
          - "Take-Off Location":  "lon,lat,alt"
          - "Sensitive Area":     "lon,lat lon,lat ..."
          - "Survey Area":        "lon,lat lon,lat ..."
          - "Flight Region":      "lon,lat lon,lat ..."
        """
        tree = ET.parse(file_path)
        root = tree.getroot()
        ns = {'kml': 'http://www.opengis.net/kml/2.2',
              'gx': 'http://www.google.com/kml/ext/2.2'}

        attributes = {
            "Take-Off Location": None,
            "Sensitive Area": None,
            "Survey Area": None,
            "Flight Region": None
        }

        for placemark in root.findall('.//kml:Placemark', ns):
            name_elem = placemark.find('kml:name', ns)
            if name_elem is None:
                continue
            name = name_elem.text.strip()
            if name in attributes:
                # Check for Point
                point_elem = placemark.find('.//kml:Point', ns)
                if point_elem is not None:
                    coords_elem = point_elem.find('kml:coordinates', ns)
                    if coords_elem is not None and coords_elem.text:
                        attributes[name] = coords_elem.text.strip()
                # Check for Polygon
                polygon_elem = placemark.find('.//kml:Polygon', ns)
                if polygon_elem is not None:
                    coords_elem = polygon_elem.find('.//kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', ns)
                    if coords_elem is not None and coords_elem.text:
                        attributes[name] = coords_elem.text.strip()
        return attributes
