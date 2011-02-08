#!/usr/bin/env python

''' This script uploads PDFs, Audio and Videos from current directory to www.archive.org
'''

import os
import shutil
from fnmatch import fnmatch
from subprocess import call
import urllib2
from logbook import debug, info, warn, error
import settings
from utils import start_logging, remove_extn, slugify, headify


def initialize():
    if not settings.title:
        cwd = os.path.basename(os.getcwd())
        settings.title = headify(cwd)

    if not settings.bucket:
        settings.bucket = slugify(settings.title)

    if not os.path.exists('processed/'):
        os.mkdir('processed')


def move(item):
    shutil.move(item, 'processed/')


def upload(item, mediatype, collection, keywords, url_suffix):
    info('Processing ' + item)

    cmd = []

    def add(key, value):
        cmd.append('--header')
        cmd.append(str(key) + ':' + str(value))

    #cmd.append('echo') # for testing
    cmd.append('curl')
    cmd.append('--location')

    add('x-archive-auto-make-bucket', 1)
    add('x-archive-ignore-preexisting-bucket', 1)
    add('authorization', ' LOW ' + settings.access_key + ':' + settings.secret_key)
    add('x-archive-meta-mediatype', mediatype)
    add('x-archive-meta-collection', collection)
    add('x-archive-meta-title', settings.title)
    add('x-archive-meta-description', settings.description)
    add('x-archive-meta-creator', settings.creator)
    add('x-archive-meta-date', settings.date)
    add('x-archive-meta-subject', keywords)
    add('x-archive-meta-licenseurl', 'http://creativecommons.org/licenses/by-nc/3.0/')

    cmd.append('--progress-bar')
    #cmd.append('--max-time')
    #cmd.append('3600')
    #cmd.append('--retry')
    #cmd.append('3')
    #cmd.append('--verbose')
    cmd.append('--output')
    cmd.append(item + '.log')
    cmd.append('--upload-file')
    cmd.append(item)
    cmd.append('http://s3.us.archive.org/' + settings.bucket + url_suffix + '/' + urllib2.quote(item))

    try:
        call(cmd)
    except KeyboardInterrupt:
        # Sometimes curl is hanging even after uploading the item is 100% done.
        # In that case, I have to press ctrl+c to continue with next item.
        pass

    move(item)
    info('Finished ' + item)



def get_keywords(pattern, mediatype):
    kw = [settings.title, mediatype, settings.creator]
    items = os.listdir(os.curdir) + os.listdir('processed')
    for item in items:
        if fnmatch(item, pattern):
            cleaned_item = headify(item)
            kw.append(cleaned_item)

    return '; '.join(kw).title()


def process(pattern, mediatype, collection, url_suffix=''):
    keywords = get_keywords(pattern, mediatype)
    items = sorted(os.listdir(os.curdir))
    for item in items:
        if fnmatch(item, pattern):
            upload(item, mediatype, collection, keywords, url_suffix)


def main():
    initialize()

    process('*.pdf', 'texts', 'opensource', '')
    process('*.mp3', 'audio', 'opensource_audio', '-audio')
    process('*.mp4', 'movies', 'opensource_movies', '-videos')


if __name__ == "__main__":
    import sys

    start_logging(__file__)
    sys.exit(main())
