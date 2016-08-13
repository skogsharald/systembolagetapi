# -*- coding: utf-8 -*-
from flask import jsonify, abort, request
from systembolagetapi_app import app
from bs4 import BeautifulSoup
import requests


def find_intersect(lists):
    """
    Finds the intersection of multiple lists.
    :param lists: list of the type [[1,3,4],[1,2,3],[1,3,5]].
    :return: The intersection of lists (e.g. [1,3])
    """
    sets = iter(lists)
    result = next(sets)
    for s in sets:
        result = result.intersection(s)
    return result


@app.route('/systembolaget/api/articles', methods=['GET'])
def get_products():
    if request.args:
        possible_results = []
        possible_results_ids = []
        for query, value in request.args.iteritems():
            partial_results = []
            partial_results_ids = set()
            values = value.split(',')  # Comma-separated -> list
            for v in values:
                for article in app.sb_articles:
                    found = False
                    if article['article_id'] not in partial_results_ids:
                        # Bool must be before int as isinstance(False, int) == True
                        if isinstance(article[query], bool):
                            # Both True and 1 OR False and 0
                            if article[query] and (v == "true" or v == "1"):
                                found = True
                            elif not article[query] and (v == "false" or v == "0"):
                                found = True
                        elif isinstance(article[query], str) and article[query].lower() == v.lower():
                            found = True
                        elif isinstance(article[query], int) and article[query] == int(v):
                            found = True
                        elif isinstance(article[query], float) and article[query] == float(v):
                            found = True
                    if found:
                        partial_results.append(article)
                        partial_results_ids.add(article['article_id'])
            possible_results.extend(partial_results)
            possible_results_ids.append(partial_results_ids)
        results_ids_intersect = find_intersect(possible_results_ids)
        results = [res for res in possible_results if res['article_id'] in results_ids_intersect]



        """
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
        """
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
