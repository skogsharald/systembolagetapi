# -*- coding: utf-8 -*-
from flask import jsonify, abort, request
from systembolagetapi_app import app, cache
from systembolagetapi_app.config import PAGINATION_LIMIT, CACHE_TIMEOUT
import systembolagetapi_app.db_interface as db_interface
import re


@app.route('/systembolaget/api/stock', methods=['GET'])
def get_stock():
    offset = int(request.args.get('offset', 0))
    if offset < 0 or not isinstance(offset, int) or isinstance(offset, bool):  # isinstance(True, int) == True...
        abort(400)
    stock = db_interface.get_stock()
    encoded_url = request.url.replace(' ', '%20')  # Replace all spaces in the URL string (why are they even there?)
    next_offset = offset + min(PAGINATION_LIMIT, len(stock[offset:]))  # Find the next offset value
    if offset == 0:
        # Append the offset value to the URL string
        if len(stock[next_offset:]) == 0:
            next_url = None
        else:
            next_url = '%s&offset=%s' % (encoded_url, next_offset)
        prev_url = None
    else:
        # Replace the offset value in the URL string
        if len(stock[next_offset:]) == 0:
            next_url = None
        else:
            next_url = re.sub(r'offset=\d+', 'offset=%s' % next_offset, encoded_url)

        if offset-PAGINATION_LIMIT <= 0:
            prev_url = re.sub(r'&offset=\d+', '', encoded_url)
            if prev_url == encoded_url:
                prev_url = re.sub(r'\?offset=\d+', '', encoded_url)
        else:
            prev_url = re.sub(r'&offset=\d+', '&offset=%s' % (offset-PAGINATION_LIMIT), encoded_url)
    meta = {'count': len(stock[offset:next_offset]),
            'offset': offset,
            'total_count': len(stock),
            'next': next_url.encode('utf-8') if next_url is not None else next_url,
            'previous': prev_url.encode('utf-8') if prev_url is not None else prev_url
            }
    return jsonify({'stock': stock[offset:next_offset], 'meta': meta})


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
    meta = {'count': len(store_list)}
    return jsonify({'stock': store_list, 'meta': meta})
