
class ZoneBroadcaster:
    def __init__(self):
        self.zones = []

    def set_zones(self, zones):
        self.zones = zones

    def get_zone(self, zone_name):
        for zone in self.zones:
            if zone.name == zone_name:
                return zone
        return None

    def get_zones_by_position(self, x, y):
        possible_zones = []
        for zone in self.zones:
            if zone.is_within_coverage(x, y):
                possible_zones.append(zone)
        return possible_zones

    @staticmethod
    def broadcast_to_zones(target_zones, user_node, task):
        offers = []
        for zone in target_zones:
            offer = zone.create_offer(user_node, task)
            if offer:
                offers.append(offer)
        return offers
