#!/usr/bin/env python

''' This script uploads PDFs, Audio and Videos from current directory to www.archive.org
'''

from datetime import datetime
from logbook import debug, info, warn, error
from configobj import ConfigObj
import settings
import utils
import archive


config = ConfigObj(settings.archivedotorg_config, write_empty_values=True)


def items_to_upload():
    for item in config['items']:
        if not config['items'][item]:
            yield item


def mark_as_processed(item):
    debug("Updating config for " + item)

    config.reload()
    config['items'][item] = str(datetime.now())
    config.write()


def main():
    bucket = config['bucket']['id']
    archive.create_bucket(bucket,
                          title=config['bucket']['title'],
                          description=config['bucket']['description'],
                          date=config['bucket']['date'],
                          keywords=config['bucket']['keywords'],
                          mediatype=config['bucket']['mediatype']
                         )

    for item in items_to_upload():
        archive.upload(bucket, item)
        mark_as_processed(item)


if __name__ == "__main__":
    utils.start_logging(__file__)
    main()
