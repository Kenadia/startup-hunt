#!/usr/bin/python2.7
from collections import defaultdict
import argparse
import json
import requests
import sys
import tempfile

import angel

import pprint

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfpage import PDFPage


def pp(x):
    pprint.PrettyPrinter(indent=4).pprint(x)


def p(s):
    sys.stdout.write(s)
    sys.stdout.flush()


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
    context = candidate, matches, startups_dict

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
        # fp = open(candidate['resume'])
        with tempfile.SpooledTemporaryFile() as fp:
        # with open('output.pdf', 'wb') as fp:
            response = requests.get(candidate['resume'], stream=True)
            if response.ok:
                for block in response.iter_content(1024):
                    if not block:
                        break
                    fp.write(block)
            fp.seek(0)
            resource_manager = PDFResourceManager()
            converter = TextConverter(resource_manager, sys.stdout,
                                      codec='utf-8', laparams=LAParams())
            interpreter = PDFPageInterpreter(resource_manager, converter)
            for page in PDFPage.get_pages(fp):
                interpreter.process_page(page)
            fp.close()
            converter.close()
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
