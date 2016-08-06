# -*- coding: utf-8 -*-
from flask import jsonify, abort, request
from systembolagetapi_app import app, cache
from systembolagetapi_app.config import CACHE_TIMEOUT
from bs4 import BeautifulSoup
import requests
import json


@app.route('/systembolaget/api/articles', methods=['GET'])
def get_products():
    return jsonify({'articles': app.sb_articles})


@app.route('/systembolaget/api/articles/<string:article_number>', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT)
def get_product(article_number):
    matching_article = next((article for article in app.sb_articles if article['article_id'] == article_number), None)
    if not matching_article:
        # Try again with the article number instead of ID
        matching_article = next((article for article in app.sb_articles if article['article_number'] == article_number),
                                None)
        if not matching_article:
            abort(404)
    image_url = None
    description = None
    try:
        r = requests.get(matching_article['sb_url'])
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
    matching_article['description'] = description
    matching_article['image_url'] = image_url
    return jsonify(matching_article)


@app.route('/systembolaget/api/articles/departments', methods=['GET'])
def get_departments():
    depts_set = set()
    depts = []
    for article in app.sb_articles:
        if not article['article_department'] in depts_set:
            depts.append('%s, %s' % (article['article_department'], article['name']))
            depts_set.add(article['article_department'])
    if not depts:
        abort(404)
    return make_response(jsonify({'departments': list(depts_set)}))
