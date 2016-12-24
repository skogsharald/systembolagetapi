# -*- coding: utf-8 -*-
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import urlparse
import json
import traceback

urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])


def insert_item(temp_item, table):
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cur = conn.cursor()
        # We only want to insert not-None values
        notnull = {k: v for k, v in temp_item.iteritems() if v is not None}
        query = "INSERT INTO %s (%s) VALUES%%s" % (table, ', '.join(notnull.keys()))
        cur.execute(query, (tuple([json.dumps(x) if isinstance(x, dict) else str(x) if isinstance(x, list) else x for x
                                   in notnull.values()]),))
        conn.commit()
    except Exception:
        if cur is not None and conn is not None:
            conn.rollback()
        #raise  # Re-raise the last exception
    finally:
        if cur is not None and conn is not None:
            cur.close()
            conn.close()


def get_articles(value=None, col='article_id'):
    conn = None
    cur = None
    res = []
    try:
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
        if value is not None:
            query = "SELECT * FROM articles WHERE %s = \'%s\'" % (col, value)
        else:
            query = "SELECT * FROM articles"
        cur.execute(query)
        tmp_res = cur.fetchall()
        # Make sure we get the string results as unicode
        for r in tmp_res:
            tmp_new = {}
            for k, v in r.iteritems():
                if isinstance(v, str):
                    tmp_new[k] = v.decode('utf-8')
                else:
                    tmp_new[k] = v
            res.append(tmp_new)
    except Exception:
        if cur is not None and conn is not None:
            conn.rollback()
        traceback.print_exc()
        raise  # Re-raise the last exception
    finally:
        if cur is not None and conn is not None:
            cur.close()
            conn.close()
        return res


def get_stores(store_id=None):
    conn = None
    cur = None
    res = []
    try:
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
        if store_id is not None:
            query = "SELECT * FROM stores WHERE store_id = \'%s\'" % store_id
        else:
            query = "SELECT * FROM stores"
        cur.execute(query)
        res = cur.fetchall()

    except Exception:
        if cur is not None and conn is not None:
            conn.rollback()
        raise  # Re-raise the last exception
    finally:
        if cur is not None and conn is not None:
            cur.close()
            conn.close()
        return res


def get_stock(store_id=None):
    conn = None
    cur = None
    res = []
    try:
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
        if store_id is not None:
            query = "SELECT * FROM stock WHERE store_id = \'%s\'" % store_id
        else:
            query = "SELECT * FROM stock"
        cur.execute(query)
        res = cur.fetchall()

    except Exception:
        if cur is not None and conn is not None:
            conn.rollback()
        raise  # Re-raise the last exception
    finally:
        if cur is not None and conn is not None:
            cur.close()
            conn.close()
        return res


def get_suffices():
    conn = None
    cur = None
    res = []
    try:
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
        query = "SELECT * FROM suffices"
        cur.execute(query)
        res = cur.fetchall()
    except Exception:
        if cur is not None and conn is not None:
            conn.rollback()
        raise  # Re-raise the last exception
    finally:
        if cur is not None and conn is not None:
            cur.close()
            conn.close()
        return res
