# -*- coding: utf-8 -*-
from flask import jsonify, abort, request
from systembolagetapi_app import app, cache
from systembolagetapi_app.config import PAGINATION_LIMIT, CACHE_TIMEOUT
import systembolagetapi_app.db_interface as db_interface


@app.route('/systembolaget/api/stores', methods=['GET'])
def get_stores():
    # TODO: Search on search words in store
    # TODO: Search on GPS coordinates? I.e. all stores within a rectangle
    stores = db_interface.get_stores()
    try:
        offset = int(request.args.get('offset', 0))
    except ValueError:
        abort(400)
    else:
        next_offset = offset + PAGINATION_LIMIT
        # TODO: META
        return jsonify({'stores': stores[offset:next_offset], 'next_offset': next_offset})


@app.route('/systembolaget/api/stores/<string:store_id>', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT)
def get_store(store_id):
    matching_store = db_interface.get_stores(store_id)
    if not matching_store:
        abort(404)
    return jsonify(matching_store[0])
