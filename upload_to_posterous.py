#!/usr/bin/env python

''' This script posts a video to Posterous site
'''

import os
import sys
from datetime import datetime
from subprocess import call
import urlparse
from logbook import debug, info, warn, error, critical
from configobj import ConfigObj
import settings
import utils
import posterous


config = ConfigObj(settings.posterous_config, write_empty_values=True)


def items_to_upload():
    for item in config:
        if not config[item].get('processed'):
            yield item


def update(item, post_id):
    debug("Updating config for " + item)

    config.reload()
    config[item]['processed'] = 1
    config[item]['post id'] = post_id
    config[item]['posted on'] = str(datetime.now())
    config.write()


def main():
    for item in items_to_upload():
        debug('=' * 60)
        filename = utils.download(item)
        post_id = posterous.post(title=config[item]['title'],
                                 tags=config[item]['tags'],
                                 media=filename)
        update(item, post_id)


if __name__ == "__main__":
    utils.start_logging(__file__)
    main()
