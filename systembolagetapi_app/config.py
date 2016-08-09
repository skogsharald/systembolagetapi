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
PAGINATION_LIMIT = 15
ARTICLE_URI_KEY = {
    u'Alkoholfritt': 'alkoholfritt',
    u'Likör': 'sprit',
    u'Rosé': 'rosevin',
    u'Sake': 'aperitif-dessert',
    u'Calvados': 'sprit',
    u'Fruktvin': 'aperitif-dessert',
    u'Aniskryddad sprit': 'sprit',
    u'Gin': 'sprit',
    u'Sherry': 'aperitif-dessert',
    u'Bitter': 'sprit',
    u'Rött vin': 'roda-viner',
    u'Mjöd': 'aperitif-dessert',
    u'Brandy och Vinsprit': 'sprit',
    u'Vermouth': 'sprit',
    u'Blanddrycker': 'cider-och-blanddrycker',
    u'Grappa och Marc': 'sprit',
    u'Övrigt starkvin': 'aperitif-dessert',
    u'Kryddad sprit': 'sprit',
    u'Whisky': 'sprit',
    u'Vin av flera typer': 'aperitif-dessert',
    u'Tequila och Mezcal': 'sprit',
    u'Röda': 'roda-viner',
    u'Okryddad sprit': 'sprit',
    u'Rosévin': 'rosevin',
    u'Cider': 'cider-och-blanddrycker',
    u'Smaksatt sprit': 'sprit',
    u'Portvin': 'aperitif-dessert',
    u'Vita': 'vita-viner',
    u'Punsch': 'sprit',
    u'Armagnac': 'sprit',
    u'Aperitif': 'aperitif-dessert',
    u'Drinkar och Cocktails': 'sprit',
    u'Mousserande vin': 'mousserande-viner',
    u'Vitt vin': 'vita-viner',
    u'Rom': 'sprit',
    u'Montilla': 'aperitif-dessert',
    u'Öl': 'ol',
    u'Genever': 'sprit',
    u'Sprit av frukt': 'sprit',
    u'Cognac': 'sprit',
    u'Madeira': 'aperitif-dessert',
    u'Smaksatt vin': 'aperitif-dessert',
    u'Likör, Choklad-, kaffe- och nötter': 'sprit',
    u'Övrig sprit': 'sprit',
    u'Glögg och Glühwein': 'aperitif-dessert'
}
