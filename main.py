#!/usr/bin/python2.7
from collections import defaultdict
import json
import requests
import sys

from startup import Startup

import pprint


BASE_URL = 'https://api.angel.co/1/'
SEARCH = BASE_URL + 'search?query={query}&type={type}'
STARTUPS_BY_ID = BASE_URL + 'startups/{startup_id}'
STARTUPS_BY_TAG = BASE_URL + 'tags/{tag_id}/startups'


def pp(x):
    pprint.PrettyPrinter(indent=4).pprint(x)


def p(s):
    sys.stdout.write(s)
    sys.stdout.flush()


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


def relevance_for_context(context):
    candidate, matches, startups_dict = context

    def relevance(startup_id):
        startup = startups_dict[startup_id]
        num_matches = matches[startup_id]
        quality = startup.quality
        # print '%s - %d, %d' % (startup.name, num_matches, quality)
        return num_matches * 5 + quality
    return relevance


def print_startup(startup):
    print startup.name
    print '\tQuality: %d' % startup.quality
    print '\tLocation(s): %s' % ', '.join(map(str, startup.locations))
    print '\tMarket(s): %s' % ', '.join(map(str, startup.markets))


def main():
    candidate = json.load(sys.stdin)
    matches = defaultdict(lambda: 0)
    startups_dict = dict()
    context = candidate, matches, startups_dict

    # Search for startups according to candidate info
    for location in candidate['locationPreferences']:
        p('.')
        startups = get_startups_by_location(location)
        for startup in startups:
            matches[startup.id] += 1
            startups_dict[startup.id] = startup
    for market in candidate['marketPreferences']:
        p('.')
        startups = get_startups_by_market(market)
        for startup in startups:
            matches[startup.id] += 1
            startups_dict[startup.id] = startup
    print

    # Determine ranking of startups by relevance
    startups_list = startups_dict.keys()
    startups_list.sort(key=relevance_for_context(context))
    relevant_startups = reversed(startups_list[len(startups_list) - 10:])
    for startup_id in relevant_startups:
        startup = startups_dict[startup_id]
        print_startup(startup)


if __name__ == '__main__':
    main()
