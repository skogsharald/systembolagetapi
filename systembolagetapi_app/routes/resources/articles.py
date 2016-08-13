# -*- coding: utf-8 -*-
from flask import jsonify, abort, request
from systembolagetapi_app import app, cache
from werkzeug.datastructures import MultiDict
from systembolagetapi_app.config import PAGINATION_LIMIT, CACHE_TIMEOUT
from bs4 import BeautifulSoup
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
    possible_results = []
    possible_results_ids = []
    for query, value in args.iteritems():
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
    return results


@app.route('/systembolaget/api/articles', methods=['GET'])
def get_products():
    try:
        offset = int(request.args.get('offset', 0))
        if offset < 0 or not isinstance(offset, int) or isinstance(offset, bool):  # isinstance(True, int) == True...
            raise ValueError
        args = MultiDict(request.args)
        args.pop('offset', None)  # Remove offset if it is there
        if args:
            results = search(args)
        else:
            results = app.sb_articles
    except ValueError:
        abort(400)
    else:
        next_offset = offset + min(PAGINATION_LIMIT, len(results[offset:]))
        if offset == 0:
            if len(results[next_offset:]) == 0:
                next_url = None
            else:
                next_url = '%s&offset=%s' % (request.url, next_offset) if args else '%s?offset=%s' % (request.url,
                                                                                                      next_offset)
            prev_url = None
        else:
            if len(results[next_offset:]) == 0:
                next_url = None
            else:
                next_url = re.sub(r'offset=\d+', 'offset=%s' % next_offset, request.url)
            if offset-PAGINATION_LIMIT <= 0:
                prev_url = re.sub(r'&offset=\d+', '', request.url)
            else:
                prev_url = re.sub(r'&offset=\d+', '&offset=%s' % (offset-PAGINATION_LIMIT), request.url)
        meta = {'count': len(results[offset:next_offset]),
                'offset': offset,
                'total_count': len(results),
                'filters': args,
                'next': next_url,
                'previous': prev_url
                }
        return jsonify({'articles': results[offset:next_offset], 'meta': meta})


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
    return jsonify({'departments': list(depts_set)})
