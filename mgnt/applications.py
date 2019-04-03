# -*- coding: utf-8 -*-

__all__ = ['Index', 'Comment', 'View', 'StatRegion', 'StatCity', 'Cssapp', 'Jsapp', 'Fileapp', 'RegionsJson',
           'CitiesJson', 'CommentsJson', 'Http404']

import os.path
import json
import re
from . import logger
from . import config
from .db import DbHandler

db = DbHandler()


class MgntError(BaseException):
    pass


class Error404(MgntError):
    pass


class Error500(MgntError):
    pass


class Baseapp:
    """Virtual base class for application classes"""

    def __init__(self, environ, start_response):
        self.environ = environ
        self.start_response = start_response
        self.path = environ['PATH_INFO']

    def get_status_code(self):
        if hasattr(self, 'status_code'):
            return self.status_code
        else:
            return '500 Internal Server Error'

    def get_headers(self):
        if hasattr(self, 'headers'):
            return self.headers
        else:
            return [('Content-type', 'text/html')]

    def run(self):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        try:
            result = bytes(''.join(list(self.run())), 'utf-8')
        except AttributeError:
            self.start_response('500 Internal Server Error', self.get_headers())
            return [b'This is a placeholder for wsgi application']
        except Error404:
            self.start_response('404 File Not Found', self.get_headers())
            return [b'File Not Found']
        except Error500:
            self.start_response('500 Internal Server Error', self.get_headers())
            return [b'Internal Server Error']

        # wsgiref.simple_server does not adds Content-Length header automatically
        # not necessary with gunicorn or uwsgi
        headers = self.get_headers() + [('Content-Length', str(len(result)))]
        self.start_response(self.get_status_code(), headers)
        # self.start_response(self.get_status_code(), self.get_headers())
        return [result]


class Http404(Baseapp):
    status_code = '404 Page Not Found'

    def run(self):
        raise Error404


class Fileapp(Baseapp):
    status_code = '200 Ok'
    headers = [('Content-type', 'application/octet-stream')]

    @staticmethod
    def get_file(filename):
        filepath = os.path.join(config['static_path'], filename)
        if os.path.isfile(filepath):
            return filepath
        else:
            raise Error404

    def run(self):
        with open(self.get_file(self.args[0]), encoding='utf-8') as fh:
            content = fh.read()
        yield content


class Cssapp(Fileapp):
    headers = [('Content-type', 'text/css')]


class Jsapp(Fileapp):
    headers = [('Content-type', 'text/javascript')]


class Templateapp(Baseapp):
    headers = [('Content-type', 'text/html')]
    status_code = '200 Ok'

    def get_content(self):
        return {'title': 'Template title', 'body': 'Template body'}

    def get_template(self):
        if hasattr(self, 'template'):
            return os.path.join(config['templates_path'], self.template)
        else:
            return os.path.join(config['templates_path'], 'base.html')

    def run(self):
        with open(self.get_template(), encoding='utf-8') as fh:
            yield fh.read().format(**self.get_content())


class Index(Templateapp):
    template = 'index.html'


class Comment(Templateapp):
    template = 'comment.html'


class View(Templateapp):
    template = 'view.html'


class StatRegion(Templateapp):
    template = 'stat.html'

    def get_content(self):
        content = super(self.__class__, self).get_content()
        regions = db.q('select count(co.id) as cnt, re.name, re.id '
                       'from comments co join cities ci on co.city=ci.id '
                       'join regions re on ci.region=re.id '
                       'group by re.name')
        content['tbody'] = ' '.join(
            [
                '<tr><td><a href="/statcity/{2}">{1}</a></td><td>{0}</td></tr>'.format(i[0], i[1], i[2])
                for i in regions if i[0] > 5
            ]
        )
        return content


class StatCity(Templateapp):
    template = 'stat.html'

    def get_content(self):
        content = super(self.__class__, self).get_content()
        regions = db.q('select count(co.id) as cnt, ci.name, re.id '
                       'from comments co join cities ci on co.city=ci.id '
                       'join regions re on ci.region=re.id '
                       'group by ci.name')
        content['tbody'] = ' '.join(
            [
                '<tr><td>{1}</td><td>{0}</td></tr><!-- {2} -->'.format(i[0], i[1], i[2])
                for i in regions if int(i[2]) == int(self.args[0])
            ]
        )
        return content


class Jsonapp(Baseapp):
    status_code = '200 Ok'
    headers = [('Content-type', 'application/json; charset=utf-8')]

    def run(self):
        if hasattr(self, 'json_run'):
            try:
                yield json.dumps({
                    'error': False,
                    'data': self.json_run()
                })
            except BaseException as e:
                logger.exception(e)
                yield json.dumps({
                    'error': str(e),
                    'data': None
                })
        else:
            yield json.dumps({'error': True, 'exception': 'json_run method is not defined'})


class RegionsJson(Jsonapp):
    @staticmethod
    def json_run():
        return {i[0]: i[1] for i in db.q('select id, name from regions')}


class CitiesJson(Jsonapp):
    def json_run(self):
        region_id = int(self.kwargs['region'][0])
        return {i[0]: i[1] for i in db.q('select id, name from cities where region=?', [region_id])}


class CommentsJson(Jsonapp):
    def json_run(self):
        try:
            action = self.kwargs['action'][0]
        except KeyError:
            action = None

        if action == 'add':
            # replace non-required fields with None value
            for i in ['pname', 'phone', 'email']:
                try:
                    self.kwargs[i]
                except KeyError:
                    self.kwargs[i] = [None]

            # check for field correctness
            if not (self.kwargs['email'][0] is None) and \
                    not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", self.kwargs['email'][0]):
                raise KeyError('email')
            if not (self.kwargs['phone'][0] is None) and \
                    not re.match(r"^\(\d{3}\)\d{7,10}$", self.kwargs['phone'][0]):
                raise KeyError('phone')

            logger.info('Adding comment '
                        'sname={sname}, '
                        'fname={fname}, '
                        'pname={pname}, '
                        'city={city}, '
                        'phone={phone}, '
                        'email={email}, '
                        'comment={comment}'
                        ''.format(sname=self.kwargs['sname'][0],
                                  fname=self.kwargs['fname'][0],
                                  pname=self.kwargs['pname'][0],
                                  city=self.kwargs['city'][0],
                                  phone=self.kwargs['phone'][0],
                                  email=self.kwargs['email'][0],
                                  comment=self.kwargs['comment'][0],
                                  )
                        )

            db.q('insert into comments (sname, fname, pname, city, phone, email, comment) values '
                 '(?, ?, ?, ?, ?, ?, ?)',
                 [
                     self.kwargs['sname'][0],
                     self.kwargs['fname'][0],
                     self.kwargs['pname'][0],
                     self.kwargs['city'][0],
                     self.kwargs['phone'][0],
                     self.kwargs['email'][0],
                     self.kwargs['comment'][0],
                 ]
                 )
            return True
        elif action == 'del':
            logger.info('Deleting comment with id {0}'.format(self.kwargs['id'][0]))
            db.q('delete from comments where id = ?', self.kwargs['id'])
            return True
        else:
            return {
                i[0]: {
                    'sname': i[1],
                    'fname': i[2],
                    'pname': i[3],
                    'city': i[4],
                    'phone': i[5],
                    'email': i[6],
                    'comment': i[7]
                } for i in db.q('select co.id, co.sname, co.fname, co.pname, ci.name, co.phone, co.email, co.comment'
                                ' from comments co, cities ci where ci.id=co.city')}
