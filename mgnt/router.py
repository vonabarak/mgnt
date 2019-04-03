# -*- coding: utf-8 -*-

from . import logger
from .applications import *
import re
import urllib.parse as parse


views = (
    (r'^/$', Index),
    (r'^/comment/$', Comment),
    (r'^/view/$', View),
    (r'^/stat/$', StatRegion),
    (r'^/statcity/(\d+)$', StatCity),
    (r'^/static/(.+\.css)$', Cssapp),
    (r'^/static/(.+\.js)$', Jsapp),
    (r'^/static/(.+)$', Fileapp),
    (r'^/api/regions/$', RegionsJson),
    (r'^/api/cities/$', CitiesJson),
    (r'^/api/comments/$', CommentsJson),

)


def start(environ, start_response):
    url = environ['PATH_INFO']
    query = parse.parse_qs(environ['QUERY_STRING'], keep_blank_values=False)
    logger.debug('Requested URL: {0}'.format(url))
    for regexp, app in views:
        if re.search(regexp, url):
            logger.debug('Running application {0}'.format(app))
            return app(environ, start_response)(*re.match(regexp, url).groups(), **query)
    logger.info('404 Page not found')
    return Http404(environ, start_response)()
