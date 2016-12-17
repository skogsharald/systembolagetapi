# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.cache import Cache
from preprocessing.init_resources import get_resources

app = Flask(__name__)
app.sb_articles, app.sb_stores, app.sb_stock, app.suffix_set = get_resources(test=False)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

BOTTLE = '03'
CAN = '12'

from systembolagetapi_app.routes.resources import articles, stores, stock
from systembolagetapi_app.routes.handlers import errors