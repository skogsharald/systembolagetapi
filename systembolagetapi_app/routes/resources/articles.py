# -*- coding: utf-8 -*-
from flask import jsonify, abort
from systembolagetapi_app import app, sb_articles
import bs4 as bs


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

@app.route('/systembolaget/api/articles/departments', methods=['GET'])
def get_department():
	depts_set = set()
	depts = []
	for article in sb_articles:
		if not article['article_department'] in depts_set:
			depts.append('%s, %s' % (article['article_department'], article['name']))
			depts_set.add(article['article_department'])
	if not depts:
		abort(404)
	return jsonify({'departments' : depts})