# -*- coding: utf-8 -*-
from flask import jsonify, abort, request
from systembolagetapi_app import app, cache
from systembolagetapi_app.config import PAGINATION_LIMIT, CACHE_TIMEOUT


@app.route('/systembolaget/api/stock', methods=['GET'])
def get_stock():
    try:
        offset = int(request.args.get('offset', 0))
    except ValueError:
        abort(400)
    else:
        next_offset = offset + PAGINATION_LIMIT
        return jsonify({'stock': app.sb_stock[offset:next_offset], 'next_offset': next_offset})


@app.route('/systembolaget/api/stock/store/<string:store_id>', methods=['GET'])
def get_store_stock(store_id):
    matching_store = next((store for store in app.sb_stock if store['store_id'] == store_id), None)
    if not matching_store:
        abort(404)
    return jsonify({'stock': matching_store})


@app.route('/systembolaget/api/stock/article/<string:product_id>', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT)
def get_product_stores(product_id):
    store_list = []
    for store in app.sb_stock:
        if product_id in store['article_number']:
            store_list.append(store['store_id'])
    if not store_list:
        # Search with all suffixes in suffix set, user put in the article ID, not a specific article number
        for suffix in app.suffix_set:
            for store in app.sb_stock:
                if product_id + suffix in store['article_number']:
                    store_list.append(store['store_id'])
        if not store_list:
            abort(404)
    return jsonify({'stock': store_list})