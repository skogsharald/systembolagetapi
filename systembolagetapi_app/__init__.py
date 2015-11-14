# -*- coding: utf-8 -*-
from flask import Flask
from systembolagetapi_app.preprocessing.init_resources import get_resources

app = Flask(__name__)

BOTTLE = '03'
CAN = '12'
sb_articles, sb_stores, sb_stock, suffix_set = get_resources()

from systembolagetapi_app.routes.resources import articles, stores, stock
from systembolagetapi_app.routes.handlers import errors
