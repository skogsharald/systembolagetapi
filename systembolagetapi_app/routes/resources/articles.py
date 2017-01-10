# -*- coding: utf-8 -*-
from flask import jsonify, abort, request
from systembolagetapi_app import app, cache
from werkzeug.datastructures import MultiDict
from systembolagetapi_app.config import PAGINATION_LIMIT, CACHE_TIMEOUT
import systembolagetapi_app.db_interface as db_interface
from bs4 import BeautifulSoup
import requests
import re
import json


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


def _search(args):
    possible_results = []  # Full article json objects, may be duplicates
    possible_results_ids = []  # Article id's of above objects
    for query in args:
        partial_results = []  # Results of this query
        partial_results_ids = set()  # Set containing the article id's of this query
        for v in args.getlist(query):  # The different values for this query in the MultiDict
            articles = db_interface.get_articles(v, query)
            if isinstance(v, str) or isinstance(v, unicode):  # Also search with upper case and capitalized words

                articles.extend(db_interface.get_articles(v.upper(), query))
                articles.extend(db_interface.get_articles(v.title(), query))
            for article in articles:
                partial_results.append(article)
                partial_results_ids.add(article['article_id'])
        # Add the results of the query to the possible result lists
        possible_results.extend(partial_results)
        possible_results_ids.append(partial_results_ids)
    # Find intersections in the id lists to find only unique id's
    results_ids_intersect = find_intersect(possible_results_ids)
    # Use this intersection list to single out the unique articles
    results = []
    for res in possible_results:
        if res['article_id'] in results_ids_intersect:
            results_ids_intersect.remove(res['article_id'])
            results.append(res)
    return results


@app.route('/systembolaget/api/articles', methods=['GET'])
#@cache.cached(timeout=CACHE_TIMEOUT)
def get_articles():
    """
    Get all articles
    Query the API on articles based on a subset of their properties.
    The API returns maximally 20 articles at a time, hence the offset parameter and 'next' field of the meta object.
    ---
    tags:
        -   articles
    parameters:
        -   name: abv
            in: query
            description: Alcohol by volume
            type: integer
            format: float32
        -   name: article_department
            in: query
            description: Article department (Öl, Vitt vin, etc)
            type: string
        -   name: assortment
            in: query
            description: Store assortment (FS, BS, etc)
            type: string
        -   name: ecological
            in: query
            description:  Article is ecological/green
            type: boolean
        -   name: ethical
            in: query
            description:  Article has been produced ethically
            type: boolean
        -   name: kosher
            in: query
            description:  Article is kosher
            type: boolean
        -   name: name
            in: query
            description: The article name
            type: string
        -   name: origin_country
            in: query
            description: Country of origin
            type: string
        -   name: origin
            in: query
            description: Region of origin. Usually only exists for wines
            type: string
        -   name: packaging
            in: query
            description: The article packaging. Useful for differentiating boxed wines versus bottled, or beer in cans/kegs/bottles
            type: string
        -   name: producer
            in: query
            description: The producer of the article
            type: string
        -   name: supplier
            in: query
            description: The supplier of the article
            type: string
        -   name: volume_ml
            in: query
            type: integer
            format: float32
            description: Volume of the packaging in milliliters. Useful for differentiating large versus small bottles
        -   name: year
            in: query
            type: string
            description: The year (i.e. vintage) of the article
        -   name: offset
            in: query
            type: integer
            description: Offset the results
    responses:
        200:
            description:  Sends all articles specified by the union of the queries
            schema:
                title: articles
                type: array
                items:
                    $ref: '#/definitions/get_article_get_Article'
    """
    offset = int(request.args.get('offset', 0))
    if offset < 0 or not isinstance(offset, int) or isinstance(offset, bool):  # isinstance(True, int) == True...
        abort(400)
    # The multidict is a dict capable of containing several non-unique keys
    # (Necessary for origin=italien&origin=usa)
    args = MultiDict(request.args)
    args.pop('offset', None)  # Remove offset if it is present
    if args:
        results = _search(args)
    else:
        results = db_interface.get_articles()
    encoded_url = request.url.replace(' ', '%20')  # Replace all spaces in the URL string (why are they even there?)
    if args:
        encoded_url = unicode(encoded_url.split('?')[0])
        encoded_args = []
        for key in args:
            for value in args.getlist(key):
                encoded_args.append('%s=%s' % (key, value))
        encoded_url += '?%s' % '&'.join(encoded_args)
        if offset > 0:  # Also append the offset argument
            encoded_url += '&offset=%s' % offset
    next_offset = offset + min(PAGINATION_LIMIT, len(results[offset:]))  # Find the next offset value
    if offset == 0:
        # Append the offset value to the URL string
        if len(results[next_offset:]) == 0:
            next_url = None
        else:
            next_url = '%s&offset=%s' % (encoded_url, next_offset) if args else \
                '%s?offset=%s' % (encoded_url, next_offset)
        prev_url = None
    else:
        # Replace the offset value in the URL string
        if len(results[next_offset:]) == 0:
            next_url = None
        else:
            next_url = re.sub(r'offset=\d+', 'offset=%s' % next_offset, encoded_url)

        if offset-PAGINATION_LIMIT <= 0:
            prev_url = re.sub(r'&offset=\d+', '', encoded_url)
            if prev_url == encoded_url:
                prev_url = re.sub(r'\?offset=\d+', '', encoded_url)
        else:
            prev_url = re.sub(r'&offset=\d+', '&offset=%s' % (offset-PAGINATION_LIMIT), encoded_url)
    meta = {'count': len(results[offset:next_offset]),
            'offset': offset,
            'total_count': len(results),
            'filters': dict(args),
            'next': next_url,
            'previous': prev_url
            }
    print json.dumps(meta)
    return jsonify({'articles': results[offset:next_offset], 'meta': meta})


@app.route('/systembolaget/api/articles/<string:article_number>', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT)
def get_article(article_number):
    """
        Get a specific article
        Some articles have different numbers based on their packaging, prefixed with their article ID.
        For example, Heineken has article ID 1536. /articles/1536 gives the first matching article with that ID, in this
        case 153603 - Heineken on a 330ml bottle. /articles/153612, however, returns Heineken on a 330ml can.
        ---
        tags:
            - articles
        parameters:
            -   name: article_number
                in: path
                type: string
                description: Article ID or article number.
                required: true
        responses:
            200:
                description: Sends the article with the article ID or number
                schema:
                    id: Article
                    type: object
                    properties:
                        abv:
                            type: integer
                            format: float32
                        article_department:
                            type: string
                        article_id:
                            type: string
                        article_number:
                            type: string
                        assortment:
                            type: string
                        delivery_end:
                            type: string
                        ecological:
                            type: boolean
                        ethical:
                            type: boolean
                        internal_article_id:
                            type: string
                        kosher:
                            type: boolean
                        name:
                            type: string
                        name2:
                            type: string
                        obsolete:
                            type: boolean
                        origin:
                            type: string
                        origin_country:
                            type: string
                        packaging:
                            type: string
                        price_incl_vat:
                            type: integer
                            format: float32
                        price_per_liter:
                            type: integer
                            format: float32
                        producer:
                            type: string
                        raw_materials:
                            type: string
                        recycle_value:
                            type: string
                        sale_start:
                            type: string
                        sb_url:
                            type: string
                        seal:
                            type: string
                        supplier:
                            type: string
                        type:
                            type: string
                        uri:
                            type: string
                        volume_ml:
                            type: integer
                            format: integer32
                        year:
                            type: string
                        year_tested:
                            type: string
    """
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
    return jsonify({'article': matching_article})


@app.route('/systembolaget/api/articles/departments', methods=['GET'])
def get_departments():
    """
    Get all possible article departments
    ---
    tags:
        -   articles
    responses:
        200:
            description: List of all available article departments
            schema:
                type: array
                items:
                    type: string

    """
    depts_set = set()
    depts = []
    articles = db_interface.get_articles()
    for article in articles:
        if not article['article_department'] in depts_set:
            depts.append('%s, %s' % (article['article_department'], article['name']))
            depts_set.add(article['article_department'])
    if not depts:
        abort(404)
    return jsonify({'departments': list(depts_set), 'meta': {'count': len(depts_set)}})
