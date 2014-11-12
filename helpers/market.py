class Market:
    def __init__(self, json):
        self.id = json['id']
        self.name = json['display_name']

    def __str__(self):
        return self.name
