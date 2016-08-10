from flask import jsonify, abort, request
from systembolagetapi_app import app, sb_stores
from systembolagetapi_app.config import PAGINATION_LIMIT


@app.route('/systembolaget/api/stores', methods=['GET'])
def get_stores():
    try:
        offset = int(request.args.get('offset', 0))
    except ValueError:
        abort(400)
    next_offset = offset + PAGINATION_LIMIT
    return jsonify({'stores': sb_stores[offset:next_offset], 'next_offset': next_offset})


@app.route('/systembolaget/api/stores/<string:store_id>', methods=['GET'])
def get_store(store_id):
    matching_store = next((store for store in sb_stores if store['store_id'] == store_id), None)
    if not matching_store:
        abort(404)
    return jsonify(matching_store)
