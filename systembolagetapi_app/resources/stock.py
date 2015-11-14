from systembolagetapi_app import app, stock, suffix_set
from flask import jsonify, abort


@app.route('/systembolaget/api/stock/', methods=['GET'])
def get_stock():
    return jsonify({'stock: ': stock})


@app.route('/systembolaget/api/stock/store/<string:store_id>', methods=['GET'])
def get_store_stock(store_id):
    stock_list = [store for store in stock if store['store_id'] == store_id]
    if not stock_list:
        abort(404)
    return jsonify({'stock': stock_list})


@app.route('/systembolaget/api/stock/article/<string:product_id>', methods=['GET'])
def get_product_stores(product_id):
    store_list = []
    for store in stock:
        if product_id in store['article_id']:
            store_list.append(store['store_id'])
    if not store_list:
        # Search with all suffixes in suffix set, user put in the article ID, not a specific article number
        for suffix in suffix_set:
            for store in stock:
                if product_id + suffix in store['article_id']:
                    store_list.append(store['store_id'])
        if not store_list:
            abort(404)
    return jsonify({'stock': {'store_id': store_list}})