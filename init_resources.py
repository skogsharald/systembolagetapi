# -*- coding: utf-8 -*-
from xml.etree import ElementTree
import re
import requests
import unicodedata
import argparse
from systembolagetapi_app.config import PRODUCT_URL, STORE_URL, STORE_PRODUCT_URL, SB_ARTICLE_BASE_URL, \
    ARTICLE_URI_KEY, PRODUCT_PATH, STORE_PATH, STORE_PRODUCT_PATH
from systembolagetapi_app import db_interface
from xmldictconfig import XmlDictConfig
import traceback

hours_string_pattern = re.compile('\d{4}-\d{2}-\d{2};\d{2}:\d{2};\d{2}:\d{2}')


def internationalize(text):
    """
    Internationalizes text by replacing special characters with ascii 'equivalents'
    e.g. åäö -> aao
    :param text: Text to internationalize
    :return: Internationalized string
    """
    if not isinstance(text, unicode):
        text = unicode(text)
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')


def get_resources(args):
    func = get_resource_to_json
    if args.test:
        print '---- READING DATA FROM DISK ----'
        func = load_resource_to_json
    if args.reset:
        print '---- RESETTING DATABASE AND UPDATING DATA ----'
        db_interface.reset_db()

    preprocess_products(lower_keys(func(PRODUCT_PATH if args.test else PRODUCT_URL)))
    preprocess_stores(lower_keys(func(STORE_PATH if args.test else STORE_URL)))
    preprocess_store_products(lower_keys(func(STORE_PRODUCT_PATH if args.test else STORE_PRODUCT_URL)))


def lower_keys(x):
    if isinstance(x, list):
        return [lower_keys(v) for v in x]
    elif isinstance(x, dict):
        return dict((k.lower(), lower_keys(v)) for k, v in x.iteritems())
    else:
        return x


def preprocess_products(temp_products):
    print '---- INSERTING %s ARTICLES ----' % len(temp_products['artikel'])
    map(preprocess_article, temp_products['artikel'])


def preprocess_stores(temp_stores):
    print '---- INSERTING %s STORES ----' % len(temp_stores['butikombud'])
    map(preprocess_store, temp_stores['butikombud'])


def preprocess_store_products(temp_store_products):
    print '---- INSERTING STOCK INFO FOR %s STORES ----' % len(temp_store_products['butik'])
    for store in temp_store_products['butik']:
        db_interface.insert_item({'article_number': store['artikelnr'], 'store_id': store['butiknr']}, 'stock')


def preprocess_article(article):
    temp_article = {
        'abv': float(article.get('alkoholhalt').replace('%', '')),
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
        'price_incl_vat': float(article.get('prisinklmoms')),
        'price_per_liter': float(article.get('prisperliter')),
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
        'volume_ml': float(article.get('volymiml')),
        'recycle_value': article.get('pant'),
        'ethical': article.get('etiskt') == '1',
        'obsolete': article.get('utgått') == '1'
    }
    try:
        temp_article['sb_url'] = '%s/%s/%s-%s' % (SB_ARTICLE_BASE_URL,
                                                  ARTICLE_URI_KEY[temp_article['article_department'].lower()],
                                                  '-'.join(internationalize(temp_article['name']).replace('\'', '')
                                                           .replace('/', '').replace(':', '').lower().split()),
                                                  temp_article['article_number'])
    except KeyError, AttributeError:
        print 'Error: Could not find article URI for article department: %s.' % temp_article['article_department']
        print 'Article: %s.' % temp_article['name']
        print 'Article was NOT inserted into database.'
        traceback.print_exc()
    except AttributeError:
        try:
            temp_article['sb_url'] = '%s/%s/%s-%s' % (SB_ARTICLE_BASE_URL,
                'vara',  # <--- Some articles don't have a department, and simply have "vara" in their url
                '-'.join(internationalize(temp_article['name']).replace('\'', '')
                    .replace('/', '').replace(':', '').lower().split()),
                temp_article['article_number'])
        except:
            print 'Error: Could not find article URL.'
            print 'Article: %s.' % temp_article['name']
            print 'Article was NOT inserted into database.'
            traceback.print_exc()
    else:
        db_interface.insert_item(temp_article, 'articles')  # Insert this item into database
        db_interface.insert_item({'suffix': temp_article['article_number'][-2:],
                                  'packaging': temp_article['packaging']},
                                 'suffices')  # Insert this suffix into database, if it does not already exist


def preprocess_store(store):
    temp_store = {
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
    db_interface.insert_item(temp_store, 'stores')


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--reset', action='store_true')
    parser.add_argument('--test', action='store_true')
    get_resources(parser.parse_args())
