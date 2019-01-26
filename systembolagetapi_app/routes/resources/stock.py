# -*- coding: utf-8 -*-
from flask import jsonify, abort, request, Response
from systembolagetapi_app import app, cache
from werkzeug.datastructures import MultiDict
from utils import find_intersect
from systembolagetapi_app.config import PAGINATION_LIMIT, CACHE_TIMEOUT
import systembolagetapi_app.db_interface as db_interface
import re
import json
import traceback


@app.route('/systembolaget/api/stock', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT)
def get_stock():
    """
    Get the stock of all stores
    For all stores, returns a list of all article numbers the store keeps in stock,
    together with the store ID of the store.
    The API returns maximally 20 stores at a time, hence the offset parameter and 'next' field of the meta object.
    ---
    tags:
        -   stock
    parameters:
        -   name: offset
            in: query
            type: integer
            description: Offset the results
    responses:
        200:
            description: Sends the stock of all stores.
            schema:
                title: stock
                type: array
                items:
                    $ref: '#/definitions/get_store_stock_get_Stock'
    """
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
            next_url = '%s?offset=%s' % (encoded_url, next_offset)
        prev_url = None
    else:
        # Replace the offset value in the URL string
        if len(stock[next_offset:]) == 0:
            next_url = None
        else:
            next_url = re.sub(r'offset=\d+', 'offset=%s' % next_offset, encoded_url)

        if offset-PAGINATION_LIMIT <= 0:
            prev_url = re.sub(r'&offset=\d+', '', encoded_url)
            print prev_url, encoded_url
            if prev_url == encoded_url:
                prev_url = re.sub(r'\?offset=\d+', '', encoded_url)
        else:
            prev_url = re.sub(r'offset=\d+', '&offset=%s' % (offset-PAGINATION_LIMIT), encoded_url)
    meta = {'count': len(stock[offset:next_offset]),
            'offset': offset,
            'total_count': len(stock),
            'next': next_url,
            'previous': prev_url
            }
    resp = Response(json.dumps({'stock': stock[offset:next_offset], 'meta': meta}, indent=4), content_type='application/json; charset=utf8')
    return resp


@app.route('/systembolaget/api/stock/store/<string:store_id>', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT)
def get_store_stock(store_id):
    """
    Get the stock of a specific store
    Returns a list of all article numbers this store keeps in stock, together with the
    store ID of this store.
    ---
    tags:
        -   stock
    parameters:
        -   name: store_id
            in: path
            type: string
            description: ID of a store.
            required: True
    responses:
        200:
            description: Sends the stock of a specific store.
            schema:
                id: Stock
                type: object
                properties:
                    store_id:
                        type: string
                    article_number:
                        type: string
    """
    matching_store = db_interface.get_stock(store_id)
    if not matching_store:
        abort(404)
    resp = Response(json.dumps({'stock': matching_store[0]}, indent=4), content_type='application/json; charset=utf8')
    return resp


def _cache_key():
    return request.url.encode('utf-8')


@app.route('/systembolaget/api/stock/article/<string:article_number>', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT)
def get_product_stores(article_number):
    """
    Get the stores which keep a specific article in stock
    Returns a list of store ID's.
    ---
    tags:
        -   stock
    parameters:
        -   name: article_number
            in: path
            type: string
            description: ID or number of an article.
            required: True
    responses:
        200:
            description: Sends an array of store ID's with this article ID or number in stock.
            schema:
                type: array
                items:
                    type: string
    """
    store_list = _find_store_with_article(article_number, db_interface.get_stock(), db_interface.get_suffices())
    meta = {'count': len(store_list)}
    resp = Response(json.dumps({'stock': store_list, 'meta': meta}, indent=4), content_type='application/json; charset=utf8')
    return resp


@app.route('/systembolaget/api/stock/articles', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT, key_prefix=_cache_key)
def get_products_stores():
    """
    Get the stores which keep all articles in the GET string in stock
    Returns a list of store ID's.
    ---
    tags:
        -   stock
    parameters:
        -   name: article_number
            in: path
            type: string
            description: ID or number of an article.
            required: True
    responses:
        200:
            description: Sends an array of store ID's with all article ID's or numbers in stock.
            schema:
                type: array
                items:
                    type: string
    """
    if not request.args:
        abort(400)  # Need at least one article ID/number!
    args = MultiDict(request.args)
    article_nums = args.getlist('article_number')
    if not len(article_nums):
        abort(400)  # Same as above
    stores = []
    stock = db_interface.get_stock()
    suffices = db_interface.get_suffices()
    for article_num in article_nums:
        result_set = set()
        possible_results = _find_store_with_article(article_num, stock, suffices)
        for store_id in possible_results:
            result_set.add(store_id)
        stores.append(result_set)
    final_res = find_intersect(stores)
    meta = {'count': len(final_res)}
    resp = Response(json.dumps({'stock': list(final_res), 'meta': meta}, indent=4), content_type='application/json; charset=utf8')
    return resp


def _find_store_with_article(article_number, stock, suffices):
    try:
        store_list = []
        suffix_set = set([s['suffix'] for s in suffices])
        for store in stock:
            if article_number in store['article_number']:
                store_list.append(store['store_id'])
        if not store_list:
            # Search with all suffixes in suffix set, user put in the article ID, not a specific article number
            for suffix in suffix_set:
                for store in stock:
                    if article_number + suffix in store['article_number']:
                        store_list.append(store['store_id'])
            if not store_list:
                abort(404)
        return store_list

    except:
        traceback.print_exc()
        raise
