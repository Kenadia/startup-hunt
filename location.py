class Location:
    def __init__(self, json):
        self.id = json['id']
        self.name = json['display_name']
