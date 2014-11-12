#!/usr/bin/python2.7
#
# Author: Ken Schiller

from collections import defaultdict
import argparse
import json
import sys

from helpers import angel
from helpers import pdf


def p(s):
    sys.stdout.write(s)
    sys.stdout.flush()


def relevance_for_context(context):
    '''Given matched companies, returns a fn to rate a company's relevance.'''
    matches, startups_dict = context

    def relevance(startup_id):
        startup = startups_dict[startup_id]
        num_matches = matches[startup_id]
        quality = startup.quality
        # print '%s - %d, %d' % (startup.name, num_matches, quality)
        return num_matches * 5 + quality
    return relevance


def print_startup(startup):
    '''Print a few lines of information about a startup.'''
    print startup.name
    print '\tQuality: %d' % startup.quality
    print '\tLocation(s): %s' % ', '.join(map(str, startup.locations))
    print '\tMarket(s): %s' % ', '.join(map(str, startup.markets))


def get_dictionary(path='/usr/share/dict/words'):
    '''Reads words (by default, the built-in dictionary) into a Python dict.'''
    d = {}
    try:
        with open(path) as f:
            for line in f:
                d[line.strip().lower()] = True
    except IOError:
        print 'Warning: dictionary not found. This will cause extracting' +\
              ' useful information from a resume to take longer.'
    return d


def get_proper_nouns(s, dictionary={}):
    '''Find proper nouns in a string, given a dictionary of common words.'''
    def is_capitalized(word):
        return word[0].isupper() and not word.isupper()

    def not_common_word(word):
        w = word.lower()
        if len(w.split()) > 1:
            return True
        if w in dictionary:
            return False
        if w[-1] == 's' and w[:len(w) - 1] in dictionary:
            return False
        return True

    names = []
    words = s.split()
    i = 0
    while i < len(words):
        word = words[i]
        name = []
        while is_capitalized(word) and i < len(words):
            name.append(word)
            i += 1
            word = words[i]
        if name:
            name = ' '.join(name)
            names.append(name)
        i += 1
    return filter(not_common_word, names)


def main():
    parser = argparse.ArgumentParser(
        description='Find startups relevant to a given candidate.')
    parser.add_argument('input_file', metavar='candidate_json',
                        type=str, nargs='?',
                        help='path to a JSON file containing candidate info')
    args = parser.parse_args()

    # Load candidate info from a JSON file if given, else from standard input
    if args.input_file:
        with open(args.input_file) as f:
            candidate = json.load(f)
    else:
        candidate = json.load(sys.stdin)

    matches = defaultdict(lambda: 0)
    startups_dict = dict()
    context = matches, startups_dict

    # Search for startups according to candidate info
    if 'locationPreferences' in candidate:
        for location in candidate['locationPreferences']:
            p('.')
            startups = angel.get_startups_by_location(location)
            if startups:
                for startup in startups:
                    matches[startup.id] += 1
                    startups_dict[startup.id] = startup
    if 'marketPreferences' in candidate:
        for market in candidate['marketPreferences']:
            p('.')
            startups = angel.get_startups_by_market(market)
            if startups:
                for startup in startups:
                    matches[startup.id] += 1
                    startups_dict[startup.id] = startup
    if 'resume' in candidate:
        dictionary = get_dictionary()
        pdf_startup_ids = list()
        with pdf.get_pdf_file(candidate['resume']) as pdf_file:
            pdf_text = pdf.pdf_to_text(pdf_file)
            names = get_proper_nouns(pdf_text, dictionary)
            for name in names:
                p('.')
                startups = angel.get_startups_by_name(name)
                if startups and startups[0]['name'].lower() == name.lower():
                    pdf_startup_ids.append(startups[0]['id'])
        for pdf_startup_id in pdf_startup_ids:
            pdf_startup = angel.get_startup_by_id(pdf_startup_id)
            for market in pdf_startup.markets:
                p('.')
                startups = angel.get_startups_by_tag(market.id)
                if startups:
                    for startup in startups:
                        matches[startup.id] += 1
                        startups_dict[startup.id] = startup
    print

    # Determine ranking of startups by relevance
    startups_list = startups_dict.keys()
    startups_list.sort(key=relevance_for_context(context))
    relevant_startups = reversed(startups_list[len(startups_list) - 10:])
    for i, startup_id in enumerate(relevant_startups):
        startup = startups_dict[startup_id]
        print "%d." % (i + 1),
        print_startup(startup)


if __name__ == '__main__':
    main()
