# -*- coding: utf-8 -*-
from flask import jsonify, abort, request
from systembolagetapi_app import app, cache
from systembolagetapi_app.config import PAGINATION_LIMIT, CACHE_TIMEOUT
import systembolagetapi_app.db_interface as db_interface


@app.route('/systembolaget/api/stock', methods=['GET'])
def get_stock():
    stock = db_interface.get_stock()
    try:
        offset = int(request.args.get('offset', 0))
    except ValueError:
        abort(400)
    else:
        next_offset = offset + PAGINATION_LIMIT
        # TODO: META
        return jsonify({'stock': stock[offset:next_offset], 'next_offset': next_offset})


@app.route('/systembolaget/api/stock/store/<string:store_id>', methods=['GET'])
def get_store_stock(store_id):
    matching_store = db_interface.get_stock(store_id)
    if not matching_store:
        abort(404)
    return jsonify({'stock': matching_store[0]})


@app.route('/systembolaget/api/stock/article/<string:product_id>', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT)
def get_product_stores(product_id):
    store_list = []
    stock = db_interface.get_stock()
    suffices = db_interface.get_suffices()
    suffix_set = set([s['suffix'] for s in suffices])
    print suffix_set
    for store in stock:
        if product_id in store['article_number']:
            store_list.append(store['store_id'])
    if not store_list:
        # Search with all suffixes in suffix set, user put in the article ID, not a specific article number
        for suffix in suffix_set:
            for store in stock:
                if product_id + suffix in store['article_number']:
                    store_list.append(store['store_id'])
        if not store_list:
            abort(404)
    # TODO: META
    return jsonify({'stock': store_list})