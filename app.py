# -*- coding: utf-8 -*-
from flask import Flask, jsonify, abort, make_response, url_for
from xmldictconfig import XmlDictConfig
from xml.etree import ElementTree
import requests

app = Flask(__name__)


PRODUCT_URL = 'http://www.systembolaget.se/api/assortment/products/xml'
STORE_URL = 'http://www.systembolaget.se/api/assortment/stores/xml'
STORE_PRODUCT_URL = 'http://www.systembolaget.se/api/assortment/stock/xml'
BOTTLE = '03'
CAN = '12'

products = {}
stores = {}
store_products = {}

# TODO: Request till www.systembolaget.se/dryck/ol/'-'.join(product['namn'].split())-<product['nr']>
# Hitta div med id = product-image-carousel
# Hitta img, plocka ut src

def make_public(thing, url):
    new_thing = dict(thing)
    new_thing['uri'] = '%s/%s' % (url, thing['nr'])
    return new_thing

def get_resources():
	products = preprocess_products(lower_keys(get_resource_to_json(PRODUCT_URL)))
	stores = preprocess_stores(lower_keys(get_resource_to_json(STORE_URL)))
	store_products = preprocess_store_products(lower_keys(get_resource_to_json(STORE_PRODUCT_URL)))
	return products, stores, store_products

def lower_keys(x):
	if isinstance(x, list):
		return [lower_keys(v) for v in x]
	elif isinstance(x, dict):
		return dict((k.lower(), lower_keys(v)) for k, v in x.iteritems())
	else:
		return x

def preprocess_products(temp_products):
	return {'artikel' : [make_public(product, '/systembolagetapi/api/artikel') for product in temp_products['artikel']]}

def preprocess_stores(temp_stores):
	return {'butik' : [make_public(store, '/systembolagetapi/api/butik') for store in temp_stores['butikombud']]}

def preprocess_store_products(temp_store_products):
	return {'lager' : temp_store_products['butik']}

def get_resource_to_json(url):
	r = requests.get(url)
	root = ElementTree.fromstring(r.text.encode('utf-8'))
	xmldict = XmlDictConfig(root)
	return xmldict

@app.route('/systembolagetapi/api/artikel', methods = ['GET'])
def get_products():
	return jsonify(products)

@app.route('/systembolagetapi/api/artikel/<string:product_id>', methods = ['GET'])
def get_product(product_id):
	product = [product for product in products['artikel'] if product['varnummer'] == product_id]
	if len(product) == 0:
		abort(404)
	return jsonify({'artikel' : product[0]})

@app.route('/systembolagetapi/api/artikel/lager/<string:product_id>', methods = ['GET'])
def get_product_stores(product_id):
	store_list = []
	for store in store_products['lager']:
		if product_id in store['artikelnr']:
			store_list.append(store['butiknr'])
	if len(store_list) == 0:
		abort(404)
	return jsonify({'lager' : {'butiknr' : store_list}})

@app.route('/systembolagetapi/api/butik', methods = ['GET'])
def get_stores():
	return jsonify(stores)

@app.route('/systembolagetapi/api/butik/<string:store_id>', methods = ['GET'])
def get_store(store_id):
	store = [store for store in stores['butik'] if store['nr'] == store_id]
	if len(store) == 0:
		abort(404)
	return jsonify({'butik' : store[0]})

@app.route('/systembolagetapi/api/butik/lager/<string:store_id>', methods = ['GET'])
def get_store_stock(store_id):
	stock_list = [store for store in store_products['lager'] if store['butiknr'] == store_id] 
	if len(stock_list) == 0:
		abort(404)
	return jsonify({'lager' : stock_list})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
	products, stores, store_products = get_resources()
	app.run()
	
	