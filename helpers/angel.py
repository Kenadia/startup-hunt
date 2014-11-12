import requests
from startup import Startup


BASE_URL = 'https://api.angel.co/1/'
SEARCH = BASE_URL + 'search?query={query}&type={type}'
STARTUPS_BY_ID = BASE_URL + 'startups/{startup_id}'
STARTUPS_BY_TAG = BASE_URL + 'tags/{tag_id}/startups'


def json_to_startups(startups_json):
    '''Converts a JSON response from AngelList to a Startup object.'''
    return [Startup(x) for x in startups_json if not x['hidden']]


def get_location_id_by_name(location_name):
    '''Returns the AngelList tag id for a location.'''
    try:
        data = {
            'query': location_name,
            'type': 'LocationTag',
        }
        response = requests.get(SEARCH.format(**data))
        return response.json()[0]['id']
    except Exception as e:
        print '\nError accessing AngelList API:', e


def get_market_id_by_name(market_name):
    '''Returns the AngelList tag id for a market.'''
    try:
        data = {
            'query': market_name,
            'type': 'MarketTag',
        }
        response = requests.get(SEARCH.format(**data))
        return response.json()[0]['id']
    except Exception as e:
        print '\nError accessing AngelList API:', e


def get_startups_by_tag(tag_id):
    '''Returns up to 50 startups that match a location or market tag.'''
    try:
        data = {
            'tag_id': tag_id,
        }
        response = requests.get(STARTUPS_BY_TAG.format(**data))
        startups_json = response.json()['startups']
        return json_to_startups(startups_json)
    except Exception as e:
        print '\nError accessing AngelList API:', e


def get_startups_by_location(location_name):
    '''Returns up to 50 startups that match a location name.'''
    try:
        location_id = get_location_id_by_name(location_name)
        startups = get_startups_by_tag(location_id)
        return startups
    except Exception as e:
        print '\nError accessing AngelList API:', e


def get_startups_by_market(market_name):
    '''Returns up to 50 startups that match a market name.'''
    try:
        market_id = get_market_id_by_name(market_name)
        startups = get_startups_by_tag(market_id)
        return startups
    except Exception as e:
        print '\nError accessing AngelList API:', e


def get_startups_by_name(name):
    '''Returns data on a startup, given its name.'''
    try:
        data = {
            'query': name,
            'type': 'Startup',
        }
        response = requests.get(SEARCH.format(**data))
        return response.json()
    except Exception as e:
        print '\nError accessing AngelList API:', e


def get_startup_by_id(id):
    '''Returns data on a startup, given its AngelList id.'''
    try:
        data = {
            'startup_id': id,
        }
        response = requests.get(STARTUPS_BY_ID.format(**data))
        return Startup(response.json())
    except Exception as e:
        print '\nError accessing AngelList API:', e
