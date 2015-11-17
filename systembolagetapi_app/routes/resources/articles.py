# -*- coding: utf-8 -*-
from flask import jsonify, abort
from systembolagetapi_app import app, sb_articles
from bs4 import BeautifulSoup
import requests


@app.route('/systembolaget/api/articles', methods=['GET'])
def get_products():
    return jsonify({'articles': [{
    	'article_id': article['article_id'],
    	'name': article['name'], 
    	'uri': article['uri']
    	} for article in sb_articles
    	]})


@app.route('/systembolaget/api/articles/<string:article_number>', methods=['GET'])
def get_product(article_number):
    matching_articles = [article for article in sb_articles if article['article_id'] == article_number]
    if not matching_articles:
        # Try again with the article number instead of ID
        matching_articles = [article for article in sb_articles if article['article_number'] == article_number]
        if not matching_articles:
            abort(404)
    matched_article = matching_articles[0]
    image_url = None
    description = None
    try:
        r = requests.get(matched_article['sb_url'])
        soup = BeautifulSoup(r.text, 'html.parser')
    except:
        pass
    else:
        # TODO: Check status code maybe, abort on 404, 500, etc?
        desc = soup.findAll('p', {'class': 'description'})
        if desc:
            description = desc[0].next
        img = soup.find(id='product-image-carousel')
        if img:
            image_url = 'http:%s' % img.find('img')['src']
    matched_article['description'] = description
    matched_article['image_url'] = image_url
    return jsonify(matched_article)


@app.route('/systembolaget/api/articles/departments', methods=['GET'])
def get_departments():
    depts_set = set()
    depts = []
    for article in sb_articles:
        if not article['article_department'] in depts_set:
            depts.append('%s, %s' % (article['article_department'], article['name']))
            depts_set.add(article['article_department'])
    if not depts:
        abort(404)
    return jsonify({'departments': depts})
