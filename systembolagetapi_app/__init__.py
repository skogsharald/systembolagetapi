# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.cache import Cache

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
app.config.update(JSON_AS_ASCII=False)

BOTTLE = '03'
CAN = '12'

from systembolagetapi_app.routes.resources import articles, stores, stock
from systembolagetapi_app.routes.handlers import errors