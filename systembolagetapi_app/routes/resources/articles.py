from flask import jsonify, abort
from systembolagetapi_app import app, sb_articles


@app.route('/systembolaget/api/articles', methods=['GET'])
def get_products():
    return jsonify({'articles': sb_articles})


@app.route('/systembolaget/api/articles/<string:article_number>', methods=['GET'])
def get_product(article_number):
    matching_articles = [article for article in sb_articles if article['article_id'] == article_number]
    if not matching_articles:
        # Try again with the article number instead of ID
        matching_articles = [article for article in sb_articles if article['article_number'] == article_number]
        if not matching_articles:
            abort(404)
    return jsonify(matching_articles[0])