import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString

class Config:
    ZONE_COUNT = 4
    ZONE_COVERAGE_RADIUS = 4

class ServiceZone:
    def __init__(self, x, y, coverage_radius, name):
        self.x = x
        self.y = y
        self.coverage_radius = coverage_radius
        self.name = name

def generate_zones():
    zones = []
    positions = [(3, 3), (3, 7), (7, 3), (7, 7)]
    for i, (x, y) in enumerate(positions):
        zones.append(ServiceZone(x=x, y=y, coverage_radius=Config.ZONE_COVERAGE_RADIUS, name=f"Zone{i}"))
    return zones

def save_zones_to_xml(zones, filename):
    root = ET.Element('zones')
    for zone in zones:
        zone_elem = ET.SubElement(root, 'zone', {
            'name': zone.name,
            'x': f"{zone.x:.2f}",
            'y': f"{zone.y:.2f}",
            'coverage_radius': f"{zone.coverage_radius:.2f}"
        })

    rough_string = ET.tostring(root, 'utf-8')
    reparsed = parseString(rough_string)
    pretty_xml_as_string = reparsed.toprettyxml(indent="  ")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(pretty_xml_as_string)

zones = generate_zones()
zones_filename = 'D:\\zones_data.xml'
save_zones_to_xml(zones, zones_filename)
print(f"Data successfully saved to {zones_filename}.")