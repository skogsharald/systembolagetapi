# -*- coding: utf-8 -*-
from flask import jsonify, abort, request
from systembolagetapi_app import app, cache
from werkzeug.datastructures import MultiDict
from systembolagetapi_app.config import PAGINATION_LIMIT, CACHE_TIMEOUT
import systembolagetapi_app.db_interface as db_interface
from bs4 import BeautifulSoup
import json
import requests
import re


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


def search(args):
    possible_results = []  # Full article json objects, may be duplicates
    possible_results_ids = []  # Article id's of above objects
    for query in args:
        partial_results = []  # Results of this query
        partial_results_ids = set()  # Set containing the article id's of this query
        for v in args.getlist(query):  # The different values for this query in the MultiDict
            articles = db_interface.get_articles(v, query)
            if isinstance(v, str) or isinstance(v, unicode):
                articles.extend(db_interface.get_articles(v.upper(), query))
                articles.extend(db_interface.get_articles(v.capitalize(), query))
            else:
                articles.extend(db_interface.get_articles(v, query))
            for article in articles:
                partial_results.append(article)
                partial_results_ids.add(article['article_id'])
        # Add the results of the query to the possible result lists
        possible_results.extend(partial_results)
        possible_results_ids.append(partial_results_ids)
    # Find intersections in the id lists to find only unique id's
    results_ids_intersect = find_intersect(possible_results_ids)
    # Use this intersection list to single out the unique articles
    results = [res for res in possible_results if res['article_id'] in results_ids_intersect]
    return results


@app.route('/systembolaget/api/articles', methods=['GET'])
#@cache.cached(timeout=CACHE_TIMEOUT)
def get_products():
    try:
        offset = int(request.args.get('offset', 0))
        if offset < 0 or not isinstance(offset, int) or isinstance(offset, bool):  # isinstance(True, int) == True...
            raise ValueError
        # The multidict is a dict capable of containing several non-unique keys
        # (Necessary for origin=italien&origin=usa)
        args = MultiDict(request.args)
        args.pop('offset', None)  # Remove offset if it is
        if args:
            results = search(args)
        else:
            results = db_interface.get_articles()
    except ValueError:
        abort(400)
    else:
        encoded_url = request.url.replace(' ', '%20')  # Replace all spaces in the URL string (why are they even there?)
        if args:
            encoded_url = unicode(encoded_url.split('?')[0])
            encoded_args = []
            for key in args:
                for value in args.getlist(key):
                    encoded_args.append('%s=%s' % (key, value))
            encoded_url += u'?%s' % u'&'.join(encoded_args)
        next_offset = offset + min(PAGINATION_LIMIT, len(results[offset:]))  # Find the next offset value
        if offset == 0:
            # Append the offset value to the URL string
            if len(results[next_offset:]) == 0:
                next_url = None
            else:
                next_url = u'%s&offset=%s' % (encoded_url, next_offset) if args else \
                    u'%s?offset=%s' % (encoded_url, next_offset)
            prev_url = None
        else:
            # Replace the offset value in the URL string
            if len(results[next_offset:]) == 0:
                next_url = None
            else:
                next_url = re.sub(r'offset=\d+', 'offset=%s' % next_offset, encoded_url)

            if offset-PAGINATION_LIMIT <= 0:
                prev_url = re.sub(r'&offset=\d+', '', encoded_url)
            else:
                prev_url = re.sub(r'&offset=\d+', '&offset=%s' % (offset-PAGINATION_LIMIT), encoded_url)
        meta = {'count': len(results[offset:next_offset]),
                'offset': offset,
                'total_count': len(results),
                'filters': dict(args),
                'next': next_url,
                'previous': prev_url
                }
        return jsonify({'articles': results[offset:next_offset], 'meta': meta})


@app.route('/systembolaget/api/articles/<string:article_number>', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT)
def get_product(article_number):
    matching_articles = db_interface.get_articles(article_number)
    if not matching_articles:
        matching_articles = db_interface.get_articles(article_number, 'article_number')
    if not matching_articles:
        abort(404)
    else:
        matching_article = dict(matching_articles[0])
    """
    matching_article = next((article for article in articles if article['article_id'] == article_number), None)
    if not matching_article:
        # Try again with the article number instead of ID
        matching_article = next((article for article in articles if article['article_number'] == article_number),
                                None)
        if not matching_article:
            abort(404)
    """
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
    articles = db_interface.get_articles()
    for article in articles:
        if not article['article_department'] in depts_set:
            depts.append('%s, %s' % (article['article_department'], article['name']))
            depts_set.add(article['article_department'])
    if not depts:
        abort(404)
    return jsonify({'departments': list(depts_set)})
