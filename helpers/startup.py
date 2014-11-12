from location import Location
from market import Market


class Startup:
    def __init__(self, json):
        self.id = json['id']
        self.name = json['name']
        self.quality = json['quality']
        self.locations = [Location(x) for x in json['locations']]
        self.markets = [Market(x) for x in json['markets']]
