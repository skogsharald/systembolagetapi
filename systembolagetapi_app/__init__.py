# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.cache import Cache
from systembolagetapi_app.preprocessing.init_resources import get_resources

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
#app.config

BOTTLE = '03'
CAN = '12'
sb_articles, sb_stores, sb_stock, suffix_set = get_resources(test=True)

from systembolagetapi_app.routes.resources import articles, stores, stock
from systembolagetapi_app.routes.handlers import errors
