# coding: utf-8

import logging
import argparse
import sys
import sqlite3
import csv
import glob
from datetime import datetime, timedelta
import urllib2
import json
from readability.readability import Readability
import psycopg2
from dateutil.parser import parse as dateparse
from couchdbkit import Server, StringProperty, DateTimeProperty, Document
from couchdbkit.designer import push
from uuid import uuid4

TIMEFORMAT = "%Y%m%d"
YAHOO_API="http://query.yahooapis.com/v1/public/yql?q=%s&format=json"

class StockDocument(Document):
    url = StringProperty()
    title = StringProperty()
    content = StringProperty()
    symbol = StringProperty()
    date= DateTimeProperty()

    def gen_id(self):
        self._id = str(uuid4())
class PostgresStore:
    def __init__(self):
        self.conn = psycopg2.connect("dbname=watchdog user=watchdog")
        try:
            cur = conn.cursor()
            #cur.execute('CREATE DATABASE watchdog;')
            cur.execute("CREATE TABLE documents (id serial PRIMARY KEY, url varchar UNIQUE, title varchar, content varchar);")
        except Exception as e:
            pass


    def store_document(self,symbol,url, title, contents, date):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO documents (url, title, content, symbol, date) VALUES (%s,%s, %s, %s,%s)",
                    (url, title, contents, symbol, date))
        cur.close()
        self.conn.commit()

    def check_update(url, date):
        conn = _get_doc_dbconn()
        cur = conn.cursor()
        cur.execute("""SELECT date from documents_document where url = '%s'"""%url)
        result = cur.fetchone()
        if result:
            return False
        else:
             return True

class CouchdbStore:
    db=None
    def __init__(self):
        server = Server()
        self.db = server.get_or_create_db('stocktools')
        push('_design/stockdocument', self.db)
        print "pushed OK"
        StockDocument.set_db(self.db)

    def store_document(self,symbol,url, title, contents, date):
        sdocument = StockDocument(url=url,title=title,content=contents, date=date, symbol=symbol)
        sdocument.gen_id()
        sdocument.save()
        return sdocument

    def get_docs(self, symbol, startdate=None, enddate=None):
        pass

    def get_doc(self, url):
        results = StockDocument.view('stockdocument/byurl',key=url)
        return results



def readability(db,symbol,new):
    url = new['href']
    htmlcode = urllib2.urlopen(url).read().decode('utf-8')
    readability = Readability(htmlcode, url)
    print(readability.title, len(readability.content))
    if len(readability.content)>20000:
        logging.debug("Got large content from %s .. trimming"%url)
        content = readability.content[:20000]
    else :
        content = readability.content
    return db.store_document(symbol, new['href'],readability.title,content, new['date'])



