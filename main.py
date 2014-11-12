#!/usr/bin/python2.7
import json
import requests
import sys


def main():
    candidate = json.loads(sys.stdin)
    companies = ['Lob']
    print companies

if __name__ == '__main__':
    main()
