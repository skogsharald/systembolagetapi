# -*- coding: utf-8 -*-
from flask import Flask

app = Flask(__name__)

BOTTLE = '03'
CAN = '12'

from systembolagetapi_app.routes.resources import articles, stores, stock
from systembolagetapi_app.routes.handlers import errors