#!/usr/bin/env python

''' This script uploads PDFs, Audio and Videos from current directory to www.archive.org
'''

import os
import shutil
from fnmatch import fnmatch
from subprocess import call
import urllib2
from datetime import datetime
from logbook import debug, info, warn, error
from configobj import ConfigObj
import settings
from utils import start_logging, remove_extn, slugify, headify
import archive


config = ConfigObj(settings.archivedotorg_config, write_empty_values=True)


def items_to_upload():
    config.reload()
    for item in config['items']:
        if not config['items'][item]:
            yield item


def mark_as_processed(item):
    now = str(datetime.now())
    debug("Updating config for " + item)

    config['items'][item] = now
    config.write()


def main():
    bucket=config['bucket']['name']
    archive.create_bucket(bucket,
                          title=config['bucket']['title'],
                          description=config['bucket']['description'],
                          date=config['bucket']['date'],
                          keywords=config['bucket']['keywords'],
                          mediatype=config['bucket']['mediatype']
                         )

    for item in items_to_upload():
        archive.upload_to_archivedotorg(bucket, item)
        mark_as_processed(item)


if __name__ == "__main__":
    start_logging(__file__)
    main()
