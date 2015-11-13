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

articles = []
stores = []
stock = []
suffix_set = set()


def get_resources():
    temp_products = preprocess_products(lower_keys(get_resource_to_json(PRODUCT_URL)))
    temp_stores = preprocess_stores(lower_keys(get_resource_to_json(STORE_URL)))
    temp_store_products, temp_suffix_set = preprocess_store_products(
        lower_keys(get_resource_to_json(STORE_PRODUCT_URL)))
    return temp_products, temp_stores, temp_store_products, temp_suffix_set


def lower_keys(x):
    if isinstance(x, list):
        return [lower_keys(v) for v in x]
    elif isinstance(x, dict):
        return dict((k.lower(), lower_keys(v)) for k, v in x.iteritems())
    else:
        return x


def preprocess_products(temp_products):
    return map(preprocess_article, temp_products['artikel'])


def preprocess_stores(temp_stores):
    return map(preprocess_store, temp_stores['butikombud'])


def preprocess_store_products(temp_store_products):
    temp_suffix_set = set()
    for store in temp_store_products['butik']:
        for artikelnr in store['artikelnr']:
            temp_suffix_set.add(artikelnr[-2:])
    return [{'article_number': store['artikelnr'], 'store_id': store['butiknr']} for store in
            temp_store_products['butik']], temp_suffix_set


def preprocess_article(article):
    return {
        'abv': article.get('alkoholhalt'),
        'year': article.get('argang'),
        'internal_article_id': article.get('artikelid'),
        'ecological': article.get('ekologisk'),
        'packaging': article.get('forpackning'),
        'seal': article.get('forslutning'),
        'kosher': article.get('koscher'),
        'supplier': article.get('leverantor'),
        'name': article.get('namn'),
        'name2': article.get('namn2'),
        'article_number': article.get('nr'),
        'price_incl_vat': article.get('prisinklmoms'),
        'price_per_liter': article.get('prisperliter'),
        'producer': article.get('producent'),
        'year_tested': article.get('provadargang'),
        'raw_materials': article.get('ravarorbeskrivning'),
        'sale_start': article.get('saljstart'),
        'delivery_end': article.get('slutlev'),
        'assortment': article.get('sortiment'),
        'uri': '/systembolaget/api/article/%s' % article.get('varnummer'),
        'origin': article.get('ursprung'),
        'origin_country': article.get('ursprunglandnamn'),
        'article_id': article.get('varnummer'),
        'article_department': article.get('varugrupp'),
        'volume_ml': article.get('volymiml'),
        'recycle_value': article.get('pant')
    }


def preprocess_store(store):
    return {
        'address': store.get('address1'),
        'address2': store.get('address2'),
        'address3': store.get('address3'),
        'address4': store.get('address4'),
        'address5': store.get('address5'),
        'store_type': store.get('butikstyp'),
        'name': store.get('namn'),
        'store_id': store.get('nr'),
        'hours_open': store.get('oppettider'),
        'rt90x': store.get('rt90x'),
        'rt90y': store.get('rt90y'),
        'search_words': store.get('sokord'),
        'phone': store.get('telefon'),
        'services': store.get('tjanster'),
        'type': store.get('typ'),
        'uri': '/systembolaget/api/store/%s' % store.get('nr'),
    }


def get_resource_to_json(url):
    r = requests.get(url)
    root = ElementTree.fromstring(r.text.encode('utf-8'))
    xmldict = XmlDictConfig(root)
    return xmldict


@app.route('/systembolaget/api/articles', methods=['GET'])
def get_products():
    return jsonify({'articles': articles})


@app.route('/systembolaget/api/articles/<string:article_number>', methods=['GET'])
def get_product(article_number):
    matching_articles = [article for article in articles if article['article_id'] == article_number]
    if not matching_articles:
        # Try again with the article number instead of ID
        matching_articles = [article for article in articles if article['article_number'] == article_number]
        if not matching_articles:
            abort(404)
    return jsonify(matching_articles[0])


@app.route('/systembolaget/api/stores', methods=['GET'])
def get_stores():
    return jsonify({'stores': stores})


@app.route('/systembolaget/api/stores/<string:store_id>', methods=['GET'])
def get_store(store_id):
    store = [store for store in stores if store['store_id'] == store_id]
    if not store:
        abort(404)
    return jsonify(store[0])


@app.route('/systembolaget/api/stock/', methods=['GET'])
def get_stock():
    return jsonify({'stock: ': stock})


@app.route('/systembolaget/api/stock/store/<string:store_id>', methods=['GET'])
def get_store_stock(store_id):
    stock_list = [store for store in stock if store['store_id'] == store_id]
    if not stock_list:
        abort(404)
    return jsonify({'stock': stock_list})


@app.route('/systembolaget/api/stock/article/<string:product_id>', methods=['GET'])
def get_product_stores(product_id):
    store_list = []
    for store in stock:
        if product_id in store['article_id']:
            store_list.append(store['store_id'])
    if not store_list:
        # Search with all suffixes in suffix set, user put in the article ID, not a specific article number
        for suffix in suffix_set:
            for store in stock:
                if product_id + suffix in store['article_id']:
                    store_list.append(store['store_id'])
        if not store_list:
            abort(404)
    return jsonify({'stock': {'store_id': store_list}})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    articles, stores, stock, suffix_set = get_resources()
    app.run()
