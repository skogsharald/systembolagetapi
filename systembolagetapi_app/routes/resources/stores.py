# -*- coding: utf-8 -*-
from flask import jsonify, abort, request
from systembolagetapi_app import app, cache
from systembolagetapi_app.config import PAGINATION_LIMIT, CACHE_TIMEOUT
from werkzeug.datastructures import MultiDict
from utils import find_intersect
import datetime
import systembolagetapi_app.db_interface as db_interface
import re
import ast
import json
import traceback

DATE_FORMAT = '%Y-%m-%d %H:%M'


def _search(args):
    possible_results = []  # Full article json objects, may be duplicates
    possible_results_ids = []  # Article id's of above objects
    for query in args:
        partial_results = []  # Results of this query
        partial_results_ids = set()  # Set containing the article id's of this query
        for v in args.getlist(query):  # The different values for this query in the MultiDict
            stores = []
            if query == 'search_words':
                stores = db_interface.get_stores_search_words(v)
                stores.extend(db_interface.get_stores_search_words(v.upper()))
                stores.extend(db_interface.get_stores_search_words(v.title()))
                stores.extend(db_interface.get_stores_search_words(v.capitalize()))
            elif query == 'open':
                _stores = db_interface.get_stores()
                value = ast.literal_eval(v.title())
                if not (isinstance(value, int) or isinstance(value, bool)):
                    raise ValueError('Open query was not boolean')
                value = bool(value)  # convert so 1 -> True, 0 -> False
                now = datetime.datetime.now()
                for store in _stores:
                    if store['hours_open']:
                        store_open = False
                        date_info = ast.literal_eval(store['hours_open'])
                        for date in date_info:
                            # Build time intervals to see if store is open
                            start_str = '%s %s' % (date['date'], date['start'])
                            end_str = '%s %s' % (date['date'], date['end'])
                            start = datetime.datetime.strptime(start_str, DATE_FORMAT)
                            end = datetime.datetime.strptime(end_str, DATE_FORMAT)
                            if start <= now <= end:
                                store_open = True
                                break
                        if (value and store_open) or (not value and not store_open):
                            # Append to stores if we want only open stores or only closed stores
                            stores.append(store)
            else:
                stores = db_interface.get_stores(v, query)
                if isinstance(v, str) or isinstance(v, unicode):  # Also search with upper case and capitalized words
                    stores.extend(db_interface.get_stores(v.upper(), query))
                    stores.extend(db_interface.get_stores(v.title(), query))
            for store in stores:
                partial_results.append(store)
                partial_results_ids.add(store['store_id'])
        # Add the results of the query to the possible result lists
        possible_results.extend(partial_results)
        possible_results_ids.append(partial_results_ids)
    # Find intersections in the id lists to find only unique id's
    results_ids_intersect = find_intersect(possible_results_ids)
    # Use this intersection list to single out the unique articles
    results = []
    for res in possible_results:
        if res['store_id'] in results_ids_intersect:
            results_ids_intersect.remove(res['store_id'])
            results.append(res)
    return results


def _cache_key():
    return request.url.encode('utf-8')


@app.route('/systembolaget/api/stores', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT, key_prefix=_cache_key)
def get_stores():
    """
    Get all stores
    Query the API on stores based on a subset of their properties.
    The API returns maximally 20 stores at a time, hence the offset parameter and 'next' field of the meta object.

    **Note:** The hours_open property is actually a list of start/end objects, not string. Likewise, the search_words
     property is a list of strings.
    ---
    tags:
        -   stores
    parameters:
        -   name: search_words
            in: query
            type: string
            description: Search words such as nickname, location, etc, of store.
        -   name: open
            in: query
            type: boolean
            description: Check current time against store opening hours.
        -   name: type
            in: query
            type: string
            description: Type of store, i.e. "Butik", "Ombud", etc.
        -   name: services
            in: query
            type: string
            description: Special services provided by stores. Currently the only special service provided is 'Dryckesprovning'.
        -   name: offset
            in: query
            type: integer
            description: Offset the results.
    responses:
        200:
            description: Sends all stores specified by the union of the queries.
            schema:
                title: stores
                type: array
                items:
                    $ref: '#/definitions/get_store_get_Store'
    """
    # TODO: Search on GPS coordinates? I.e. all stores within a rectangle
    offset = int(request.args.get('offset', 0))
    if offset < 0 or not isinstance(offset, int) or isinstance(offset, bool):  # isinstance(True, int) == True...
        abort(400)
    # The multidict is a dict capable of containing several non-unique keys
    # (Necessary for origin=italien&origin=usa)
    args = MultiDict(request.args)
    args.pop('offset', None)  # Remove offset if it is present
    if args:
        # Parse so origin_country=usa,italien works as well as origin_country=usa&origin_country=italien
        # args = MultiDict({k: sum([v.split(',') for v in args.getlist(k)], []) for k in args})
        stores = _search(args)
    else:
        stores = db_interface.get_stores()
    encoded_url = request.url.replace(' ', '%20')  # Replace all spaces in the URL string (why are they even there?)

    if args:
        encoded_url = unicode(encoded_url.split('?')[0])
        encoded_args = []
        for key in args:
            for val in args.getlist(key):
                encoded_args.append('%s=%s' % (key, val))
        encoded_url += '?%s' % '&'.join(encoded_args)
        if offset > 0:  # Also append the offset argument
            encoded_url += '&offset=%s' % offset

    next_offset = offset + min(PAGINATION_LIMIT, len(stores[offset:]))  # Find the next offset value
    if offset == 0:
        # Append the offset value to the URL string
        if len(stores[next_offset:]) == 0:
            next_url = None
        else:
            next_url = '%s&offset=%s' % (encoded_url, next_offset) if args else \
                '%s?offset=%s' % (encoded_url, next_offset)
        prev_url = None
    else:
        # Replace the offset value in the URL string
        if len(stores[next_offset:]) == 0:
            next_url = None
        else:
            next_url = re.sub(r'offset=\d+', 'offset=%s' % next_offset, encoded_url)

        if offset - PAGINATION_LIMIT <= 0:
            prev_url = re.sub(r'&offset=\d+', '', encoded_url)
            if prev_url == encoded_url:
                prev_url = re.sub(r'\?offset=\d+', '', encoded_url)
        else:
            prev_url = re.sub(r'offset=\d+', 'offset=%s' % (offset - PAGINATION_LIMIT), encoded_url)
    meta = {'count': len(stores[offset:next_offset]),
            'offset': offset,
            'total_count': len(stores),
            'filters': dict(args),
            'next': unicode(next_url) if next_url else None,
            'previous': unicode(prev_url) if prev_url else None
            }

    return jsonify({'stores': stores[offset:next_offset], 'meta': meta})


@app.route('/systembolaget/api/stores/<string:store_id>', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT)
def get_store(store_id):
    """
    Get a specific store
    **Note:** The hours_open is actually a list of start/end objects, not string. Likewise, the search_words
     property is a list of strings.
    ---
    tags:
        -   stores
    parameters:
        -   name: store_id
            in: path
            type: string
            description: The ID of a specific store.
            required: True
    responses:
        200:
            description: Sends the store with the specified store ID.
            schema:
                id: Store
                type: object
                properties:
                    address:
                        type: string
                        description: Street address
                    address2:
                        type: string
                        description: Unclear...
                    address3:
                        type: string
                        description: Postal code
                    address4:
                        type: string
                        description: City
                    address5:
                        type: string
                        description: Region
                    hours_open:
                        type: string
                        description: List of start/end objects for one week
                    name:
                        type: string
                        description: Nickname of the store
                    phone:
                        type: string
                    rt90x:
                        type: string
                    rt90y:
                        type: string
                    search_words:
                        type: string
                        description: List of search-word strings
                    services:
                        type: string
                        description: A description of special services provided at this store, if any
                    store_id:
                        type: string
                    type:
                        type: string
                        description: Type of the store, i.e. "Butik", "Ombud"
                    uri:
                        type: string
    """
    matching_store = db_interface.get_stores(store_id)
    if not matching_store:
        abort(404)
    return jsonify({'store': matching_store[0]})
