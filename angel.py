import requests
from startup import Startup


BASE_URL = 'https://api.angel.co/1/'
SEARCH = BASE_URL + 'search?query={query}&type={type}'
STARTUPS_BY_ID = BASE_URL + 'startups/{startup_id}'
STARTUPS_BY_TAG = BASE_URL + 'tags/{tag_id}/startups'


def json_to_startups(startups_json):
    return [Startup(x) for x in startups_json if not x['hidden']]


def get_location_id_by_name(location_name):
    data = {
        'query': location_name,
        'type': 'LocationTag',
    }
    response = requests.get(SEARCH.format(**data))
    return response.json()[0]['id']


def get_market_id_by_name(market_name):
    data = {
        'query': market_name,
        'type': 'MarketTag',
    }
    response = requests.get(SEARCH.format(**data))
    return response.json()[0]['id']


def get_startups_by_tag(tag_id):
    '''Returns up to 50 startups that match a location or market tag.'''
    data = {
        'tag_id': tag_id,
    }
    response = requests.get(STARTUPS_BY_TAG.format(**data))
    startups_json = response.json()['startups']
    return json_to_startups(startups_json)


def get_startups_by_location(location_name):
    location_id = get_location_id_by_name(location_name)
    startups = get_startups_by_tag(location_id)
    return startups


def get_startups_by_market(market_name):
    market_id = get_market_id_by_name(market_name)
    startups = get_startups_by_tag(market_id)
    return startups
