from flask import jsonify, abort
from systembolagetapi_app import app, stores


@app.route('/systembolaget/api/stores', methods=['GET'])
def get_stores():
    return jsonify({'stores': stores})


@app.route('/systembolaget/api/stores/<string:store_id>', methods=['GET'])
def get_store(store_id):
    store = [store for store in stores if store['store_id'] == store_id]
    if not store:
        abort(404)
    return jsonify(store[0])
