# -*- coding: utf-8 -*-
from flask import Flask
from flasgger import Swagger
from flask_cache import Cache

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
app.config.update(JSON_AS_ASCII=False)

app.config['SWAGGER'] = {
    "swagger_version": "2.0",
    "title": "SystembolagetAPI",
    "headers": [
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Methods', "GET"),
        ('Access-Control-Allow-Credentials', "true"),
    ],
    "specs": [
            {
                "version": "1.0.0",
                "title": "SystembolagetAPI",
                "description": "**This example has a working backend hosted in Heroku** <br/>"
                               "You can try all HTTP operation described in this Swagger spec. <br/>"
                               "**Disclaimer:** The developer of this API is in no way affiliated with the Swedish "
                               "liqour retailer Systembolaget.",
                "endpoint": 'spec',
                "route": '/spec',
                "rule_filter": lambda rule: True  # all in
            }
        ],
    "static_url_path": "/systembolaget/api/docs",
    "specs_route": "/specs",
    "schemes": "http",
    "consumes": "text/html",
    "produces": "application/json"
}

Swagger(app)
BOTTLE = '03'
CAN = '12'

from systembolagetapi_app.routes.resources import articles, stores, stock
from systembolagetapi_app.routes.handlers import errors


@app.after_request
def after_request(response):
    if 'docs' not in response.base_url:
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', "GET")
        response.headers.add('Access-Control-Max-Age', 60 * 60 * 24 * 20)
        response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response
