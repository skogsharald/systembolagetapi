from flask import jsonify, abort
from systembolagetapi_app import app, cache
from systembolagetapi_app.config import CACHE_TIMEOUT


@app.route('/systembolaget/api/stores', methods=['GET'])
def get_stores():
    return jsonify({'stores': app.sb_stores})


@app.route('/systembolaget/api/stores/<string:store_id>', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT)
def get_store(store_id):
    matching_store = next((store for store in app.sb_stores if store['store_id'] == store_id), None)
    if not matching_store:
        abort(404)
    return jsonify(matching_store)
