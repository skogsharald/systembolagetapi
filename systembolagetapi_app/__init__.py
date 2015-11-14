# -*- coding: utf-8 -*-
from flask import Flask, jsonify, make_response
from systembolagetapi_app.preprocessing.init_resources import get_resources

app = Flask(__name__)

BOTTLE = '03'
CAN = '12'
articles, stores, stock, suffix_set = get_resources()


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


from resources import articles, stock, stores
