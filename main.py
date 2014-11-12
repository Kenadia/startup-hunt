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
    matches, startups_dict = context

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


def get_resume_file(path):
    '''Downloads file if path is an HTTP address. Returns a file pointer.'''
    if path.startswith('http'):
        fp = tempfile.SpooledTemporaryFile()
        response = requests.get(path, stream=True)
        if response.ok:
            for block in response.iter_content(1024):
                if not block:
                    break
                fp.write(block)
        fp.seek(0)
        return fp
    return open(path)


def resume_to_text(resume_file):
    with tempfile.SpooledTemporaryFile() as resume_out:
        resource_manager = PDFResourceManager()
        converter = TextConverter(resource_manager, resume_out,
                                  codec='utf-8', laparams=LAParams())
        interpreter = PDFPageInterpreter(resource_manager, converter)
        for page in PDFPage.get_pages(resume_file):
            interpreter.process_page(page)
        converter.close()
        resume_out.seek(0)
        return resume_out.read()


def get_dictionary():
    d = {}
    with open('/usr/share/dict/words') as f:
        for line in f:
            d[line.strip().lower()] = True
    return d


def get_potential_company_names(s, dictionary={}):
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
    dictionary = get_dictionary()

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
        resume_startup_ids = list()
        with get_resume_file(candidate['resume']) as resume_file:
            resume_text = resume_to_text(resume_file)
            names = get_potential_company_names(resume_text, dictionary)
            for name in names:
                p('.')
                startups = angel.get_startups_by_name(name)
                if startups and startups[0]['name'].lower() == name.lower():
                    resume_startup_ids.append(startups[0]['id'])
        for resume_startup_id in resume_startup_ids:
            resume_startup = angel.get_startup_by_id(resume_startup_id)
            for market in resume_startup.markets:
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
    for startup_id in relevant_startups:
        startup = startups_dict[startup_id]
        print_startup(startup)


if __name__ == '__main__':
    main()
