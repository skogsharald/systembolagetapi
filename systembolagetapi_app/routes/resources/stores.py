# -*- coding: utf-8 -*-
from flask import jsonify, abort, request
from systembolagetapi_app import app, cache
from systembolagetapi_app.config import PAGINATION_LIMIT, CACHE_TIMEOUT
import systembolagetapi_app.db_interface as db_interface
import re
import json


@app.route('/systembolaget/api/stores', methods=['GET'])
def get_stores():
    # TODO: Search on search words in store
    # TODO: Search on GPS coordinates? I.e. all stores within a rectangle
    # TODO: Search on all store attributes!
    offset = int(request.args.get('offset', 0))
    if offset < 0 or not isinstance(offset, int) or isinstance(offset, bool):  # isinstance(True, int) == True...
        abort(400)
    stores = db_interface.get_stores()
    encoded_url = request.url.replace(' ', '%20')  # Replace all spaces in the URL string (why are they even there?)
    next_offset = offset + min(PAGINATION_LIMIT, len(stores[offset:]))  # Find the next offset value
    if offset == 0:
        # Append the offset value to the URL string
        if len(stores[next_offset:]) == 0:
            next_url = None
        else:
            next_url = '%s&offset=%s' % (encoded_url, next_offset)
        prev_url = None
    else:
        # Replace the offset value in the URL string
        if len(stores[next_offset:]) == 0:
            next_url = None
        else:
            next_url = re.sub(r'offset=\d+', 'offset=%s' % next_offset, encoded_url)
        print offset - PAGINATION_LIMIT
        if offset - PAGINATION_LIMIT <= 0:
            prev_url = re.sub(r'&offset=\d+', '', encoded_url)
            if prev_url == encoded_url:
                prev_url = re.sub(r'\?offset=\d+', '', encoded_url)
        else:
            prev_url = re.sub(r'\?offset=\d+', '&offset=%s' % (offset - PAGINATION_LIMIT), encoded_url)
    meta = {'count': len(stores[offset:next_offset]),
            'offset': offset,
            'total_count': len(stores),
            'next': next_url.encode('utf-8') if next_url is not None else next_url,
            'previous': prev_url.encode('utf-8') if prev_url is not None else prev_url
            }
    return jsonify({'stores': stores[offset:next_offset], 'meta': meta})


@app.route('/systembolaget/api/stores/<string:store_id>', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT)
def get_store(store_id):
    matching_store = db_interface.get_stores(store_id)
    if not matching_store:
        abort(404)
    return jsonify(matching_store[0])
