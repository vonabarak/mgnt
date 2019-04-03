# -*- coding: utf-8 -*-

import os.path
import logging

# default values for config dictionary
config = {
    'dbinitscript': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mgnt.init.sql'),
    'dbfilename': '/tmp/mgnt.sqlite',
    'logfile': '/tmp/mgnt.log',
    'templates_path': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
    'static_path': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'),
}

try:
    if os.environ['mgnt_config'] and os.path.isfile(os.environ['mgnt_config']):
        with open(os.environ['mgnt_config']) as fp:
            config_ = eval(fp.read())
            config = {**config, **config_}  # merge with default values
except BaseException as e:
    print('WARNING! Using default config')
    print(e)

# print(config)

logger = logging.getLogger('mgnt')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fh = logging.FileHandler(config['logfile'])
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(logging.StreamHandler())
