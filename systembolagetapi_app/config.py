# -*- coding: utf-8 -*-
import os
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PRODUCT_PATH = os.path.join(DATA_DIR, 'products.xml')
STORE_PATH = os.path.join(DATA_DIR, 'stores.xml')
STORE_PRODUCT_PATH = os.path.join(DATA_DIR, 'stock.xml')
PRODUCT_URL = 'http://www.systembolaget.se/api/assortment/products/xml'
STORE_URL = 'http://www.systembolaget.se/api/assortment/stores/xml'
STORE_PRODUCT_URL = 'http://www.systembolaget.se/api/assortment/stock/xml'
SB_ARTICLE_BASE_URL = 'http://www.systembolaget.se/dryck'
PAGINATION_LIMIT = 20
CACHE_TIMEOUT = 3600
ARTICLES_RELOAD = 86400
ARTICLE_URI_KEY = {
    u'alkoholfritt': 'alkoholfritt',
    u'likör': 'sprit',
    u'rosé': 'rosevin',
    u'sake': 'aperitif-dessert',
    u'calvados': 'sprit',
    u'fruktvin': 'aperitif-dessert',
    u'aniskryddad sprit': 'sprit',
    u'gin': 'sprit',
    u'sherry': 'aperitif-dessert',
    u'bitter': 'sprit',
    u'rött vin': 'roda-viner',
    u'mjöd': 'aperitif-dessert',
    u'brandy och vinsprit': 'sprit',
    u'vermouth': 'sprit',
    u'blanddrycker': 'cider-och-blanddrycker',
    u'grappa och marc': 'sprit',
    u'övrigt starkvin': 'aperitif-dessert',
    u'kryddad sprit': 'sprit',
    u'whisky': 'sprit',
    u'vin av flera typer': 'aperitif-dessert',
    u'tequila och mezcal': 'sprit',
    u'röda': 'roda-viner',
    u'okryddad sprit': 'sprit',
    u'rosévin': 'rosevin',
    u'cider': 'cider-och-blanddrycker',
    u'smaksatt sprit': 'sprit',
    u'portvin': 'aperitif-dessert',
    u'vita': 'vita-viner',
    u'punsch': 'sprit',
    u'armagnac': 'sprit',
    u'aperitif': 'aperitif-dessert',
    u'drinkar och cocktails': 'sprit',
    u'mousserande vin': 'mousserande-viner',
    u'vitt vin': 'vita-viner',
    u'rom': 'sprit',
    u'montilla': 'aperitif-dessert',
    u'öl': 'ol',
    u'genever': 'sprit',
    u'sprit av frukt': 'sprit',
    u'snaps': 'sprit',
    u'cognac': 'sprit',
    u'madeira': 'aperitif-dessert',
    u'smaksatt vin': 'aperitif-dessert',
    u'likör, choklad-, kaffe- och nötter': 'sprit',
    u'övrig sprit': 'sprit',
    u'glögg och glühwein': 'aperitif-dessert',
    u'blå mousserande': 'mousserande-viner',
    u'blå stilla': 'aperitif-dessert',
    u'juldrycker': 'aperitif-dessert',
    u'akvavit och kryddat brännvin': 'sprit',
    u'anissprit': 'sprit',
    u'vodka och brännvin': 'sprit',
    u'frukt och druvsprit': 'sprit',
    u'sprit av flera typer': 'sprit',
    u'gin och genever': 'sprit',
    u'armagnac och brandy': 'sprit',
    u'presentförpackningar': 'presentartiklar',
    u'dryckestillbehör': 'presentartiklar',
    u'tillbehör': 'presentartiklar',
    u'aperitif & dessert': 'aperitif-dessert',
    u'aperitif och dessert': 'aperitif-dessert'
}
