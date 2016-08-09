# -*- coding: utf-8 -*-

from xml.etree import ElementTree
import re
import requests
from systembolagetapi_app.config import PRODUCT_URL, STORE_URL, STORE_PRODUCT_URL, SB_ARTICLE_BASE_URL, ARTICLE_URI_KEY, PRODUCT_PATH, STORE_PATH, STORE_PRODUCT_PATH
from xmldictconfig import XmlDictConfig

hours_string_pattern = re.compile('\d{4}-\d{2}-\d{2};\d{2}:\d{2};\d{2}:\d{2}')


def get_resources(test=False):
    if test:
        temp_products = preprocess_products(lower_keys(load_resource_to_json(PRODUCT_PATH)))
        temp_stores = preprocess_stores(lower_keys(load_resource_to_json(STORE_PATH)))
        temp_store_products, temp_suffix_set = preprocess_store_products(
            lower_keys(load_resource_to_json(STORE_PRODUCT_PATH)))
    else:
        temp_products = preprocess_products(lower_keys(get_resource_to_json(PRODUCT_URL)))
        temp_stores = preprocess_stores(lower_keys(get_resource_to_json(STORE_URL)))
        temp_store_products, temp_suffix_set = preprocess_store_products(
            lower_keys(get_resource_to_json(STORE_PRODUCT_URL)))
    return temp_products, temp_stores, temp_store_products, temp_suffix_set


def lower_keys(x):
    if isinstance(x, list):
        return [lower_keys(v) for v in x]
    elif isinstance(x, dict):
        return dict((k.lower(), lower_keys(v)) for k, v in x.iteritems())
    else:
        return x


def preprocess_products(temp_products):
    return map(preprocess_article, temp_products['artikel'])


def preprocess_stores(temp_stores):
    return map(preprocess_store, temp_stores['butikombud'])


def preprocess_store_products(temp_store_products):
    temp_suffix_set = set()
    for store in temp_store_products['butik']:
        for artikelnr in store['artikelnr']:
            temp_suffix_set.add(artikelnr[-2:])
    return [{'article_number': store['artikelnr'], 'store_id': store['butiknr']} for store in
            temp_store_products['butik']], temp_suffix_set


def preprocess_article(article):
    temp_article = {
        'abv': article.get('alkoholhalt').replace('%', ''),
        'year': article.get('argang'),
        'internal_article_id': article.get('artikelid'),
        'ecological': article.get('ekologisk') == '1',
        'packaging': article.get('forpackning'),
        'seal': article.get('forslutning'),
        'kosher': article.get('koscher') == '1',
        'supplier': article.get('leverantor'),
        'name': article.get('namn'),
        'name2': article.get('namn2'),
        'article_number': article.get('nr'),
        'price_incl_vat': article.get('prisinklmoms'),
        'price_per_liter': article.get('prisperliter'),
        'producer': article.get('producent'),
        'year_tested': article.get('provadargang'),
        'raw_materials': article.get('ravarorbeskrivning'),
        'sale_start': article.get('saljstart'),
        'delivery_end': article.get('slutlev'),
        'assortment': article.get('sortiment'),
        'uri': '/systembolaget/api/articles/%s' % article.get('varnummer'),
        'origin': article.get('ursprung'),
        'origin_country': article.get('ursprunglandnamn'),
        'article_id': article.get('varnummer'),
        'article_department': article.get('varugrupp'),
        'type': article.get('typ'),
        'volume_ml': article.get('volymiml'),
        'recycle_value': article.get('pant'),
        'ethical': article.get('etiskt') == '1',
        'obsolete': article.get('utgått') == '1'
    }
    temp_article['sb_url'] = '%s/%s/%s-%s' % (SB_ARTICLE_BASE_URL,
                                              ARTICLE_URI_KEY[temp_article['article_department']],
                                              '-'.join(temp_article['name'].replace('\'', '').lower().split()),
                                              temp_article['article_number'])
    return temp_article


def preprocess_store(store):
    return {
        'address': store.get('address1'),
        'address2': store.get('address2'),
        'address3': store.get('address3'),
        'address4': store.get('address4'),
        'address5': store.get('address5'),
        'store_type': store.get('butikstyp'),
        'name': store.get('namn'),
        'store_id': store.get('nr'),
        'hours_open': preprocess_hours_open(store.get('oppettider')),
        'rt90x': store.get('rt90x'),
        'rt90y': store.get('rt90y'),
        'search_words': store.get('sokord'),
        'phone': store.get('telefon'),
        'services': store.get('tjanster'),
        'type': store.get('typ'),
        'uri': '/systembolaget/api/store/%s' % store.get('nr'),
    }


def preprocess_hours_open(hours_open):
    if not hours_open:
        return None

    hours_strings = hours_string_pattern.findall(hours_open)
    hours_open_by_day = []
    for hours_string in hours_strings:
        date, start, end = hours_string.split(';')
        hours_open_by_day.append({'date': date, 'start': start, 'end': end})
    return hours_open_by_day

def get_resource_to_json(url):
    r = requests.get(url)
    root = ElementTree.fromstring(r.text.encode('utf-8'))
    return _resource_to_json(root)

def load_resource_to_json(f):
    tree = ElementTree.parse(f)
    return _resource_to_json(tree.getroot())

def _resource_to_json(root):
    xmldict = XmlDictConfig(root)
    return xmldict
