# -*- coding: utf-8 -*-
from flask import jsonify, abort, request
from systembolagetapi_app import app
from bs4 import BeautifulSoup
import requests


@app.route('/systembolaget/api/articles', methods=['GET'])
def get_products():
    print request.args
    if request.args:
        result_ids = set()
        results = []
        for query, value in request.args.iteritems():
            values = value.split(',')  # Comma-separated -> list
            if results:
                new_partial = []
                for v in values:
                    for article in results:
                        # Bool must be before int as isinstance(False, int) == True
                        if isinstance(article[query], bool):
                            # Both True and 1 OR False and 0
                            if article[query] and (v == "True" or v == "1"):
                                new_partial.append(article)
                            elif not article[query] and (v == "False" or v == "0"):
                                new_partial.append(article)
                        elif isinstance(article[query], str) and article[query].lower() == v.lower():
                            new_partial.append(article)
                        elif isinstance(article[query], int) and article[query] == int(v):
                            new_partial.append(article)
                        elif isinstance(article[query], float) and article[query] == float(v):
                            new_partial.append(article)

                results = new_partial
            else:
                for v in values:
                    for article in app.sb_articles:
                        if article['article_id'] not in result_ids:
                            # Bool must be before int as isinstance(False, int) == True
                            if isinstance(article[query], bool):
                                # Both True and 1 OR False and 0
                                if article[query] and (v == "true" or v == "1"):
                                    results.append(article)
                                    result_ids.add(article['article_id'])
                                elif not article[query] and (v == "false" or v == "0"):
                                    results.append(article)
                                    result_ids.add(article['article_id'])
                            elif isinstance(article[query], str) and article[query].lower() == v.lower():
                                results.append(article)
                                result_ids.add(article['article_id'])
                            elif isinstance(article[query], int) and article[query] == int(v):
                                results.append(article)
                                result_ids.add(article['article_id'])
                            elif isinstance(article[query], float) and article[query] == float(v):
                                results.append(article)
                                result_ids.add(article['article_id'])

        return jsonify({'articles': results})
    else:
        return jsonify({'articles': app.sb_articles})


@app.route('/systembolaget/api/articles/<string:article_number>', methods=['GET'])
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
    return jsonify({'departments': depts})
