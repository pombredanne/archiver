#!/usr/bin/env python

import pyposterous
from logbook import debug, info, warn, error, critical
import settings


def post(title, tags='', body='', media=None):
    """ Upload the given item to Posterous and return the post id.
    """
    debug("Posting " + title)

    if media:
        media = open(media)

    if isinstance(tags, list):
        tags = ','.join(tags)

    api = pyposterous.API(username=settings.posterous_username,
                          password=settings.posterous_password)

    p = api.new_post(site_name=settings.posterous_backup_sitename,
                     title=title,
                     body=body,
                     tags=tags,
                     media=media,
                     autopost=True)

    post_id = str(p.id)
    info("Posted " + title + " to Posterous. Id = " + post_id)
    return post_id
