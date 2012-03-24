# coding: utf-8

import logging
import argparse
import sys
import sqlite3
import csv
import glob
from datetime import datetime, timedelta
from fish import ProgressFish, Bird, Fish, SwimFishNoSync
import urllib2
import json
from instapaperlib import Instapaper
from readability.readability import Readability
import psycopg2
from dateutil.parser import parse as dateparse

TIMEFORMAT = "%Y%m%d"
YAHOO_API="http://query.yahooapis.com/v1/public/yql?q=%s&format=json"

def builddb(conn):
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS analytics (sym text, name text, sector text, week52high real,
                    week52low real, lastupdate real, UNIQUE(sym) ON CONFLICT REPLACE)""")
    ptotal = 0
    symbol_map = 'ASXListedCompanies.csv'
    with open(symbol_map, 'r') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i==1:continue
            cur.execute(""" INSERT INTO analytics VALUES('%s','%s','%s', %s,%s,%s)""" \
                % (row[1],row[0].replace("'","''"),row[2],0, 0,int(datetime.now().strftime(TIMEFORMAT))))
    conn.commit()
    cur.close()

def _get_dbconn():
    return sqlite3.connect('asx_analytics.db')

def _get_doc_dbconn():
    conn = psycopg2.connect("dbname=watchdog user=watchdog")
    #try:
    #    cur = conn.cursor()
    #    #cur.execute('CREATE DATABASE watchdog;')
    #    cur.execute("CREATE TABLE documents (id serial PRIMARY KEY, url varchar UNIQUE, title varchar, content varchar);")
    #except Exception as e:
    #    pass
    #finally:
    #    cur.close()
    #    conn.commit()
    return conn

def get_name_sector(symbol):
    conn = _get_dbconn()
    cur = conn.cursor()
    cur.execute("""SELECT name,sector FROM analytics WHERE sym='%s' """%symbol)
    result = cur.fetchall()
    cur.close()
    if not result:
        logging.debug("no info for %s"%symbol)
    return result[0] if result else ('','')

def get_yahoo_news(symbol):
    yqlquery = """select * from html where url="http://finance.yahoo.com/q?s=%s" and xpath='//div[@id="yfi_headlines"]/div[2]/ul/li' """% symbol
    yqlquery = urllib2.quote(yqlquery)
    results = urllib2.urlopen(YAHOO_API%yqlquery).read()
    results = json.loads(results)
    results = results['query']['results']['li']
    if not isinstance(results,list):
        results = [results,]
    news = []
    for result in results:
        try:
            href1 = result['a']['href'].strip()
            href = "".join(href1.split('*')[1:])
            if not href:
                href = href1
            href = urllib2.unquote(href)
            date = dateparse(result['cite']['span'].strip().replace('(','').replace(')',''))
            news.append(dict(title=result['a']['content'].strip(), 
                href=href, source=result['cite']['content'].strip(),
                date=date))
        except Exception as e:
            logging.exception(e)
    return news

def to_instapaper(news, instapaper_user, instapaper_pass):
    instalib = Instapaper(instapaper_user,instapaper_pass)
    status, header = instalib.auth()
    if status != 200:
        raise Exception("Instapaper login fail")
    for new in news:
        statuscode, statusmessage = instalib.add_item(new['href'], "%s - %s" % (new['title'],new['source']))
        print (statuscode)

def check_fetch(url, date):
    conn = _get_doc_dbconn()
    cur = conn.cursor()
    cur.execute("""SELECT date from documents_document where url = '%s'"""%url)
    result = cur.fetchone()
    if result:
        return False
    else:
         return True

def readability(symbol,news):
    for new in news:
        try:
            url = new['href']
            if not check_fetch(url,new['date']): continue
            htmlcode = urllib2.urlopen(url).read().decode('utf-8')
            readability = Readability(htmlcode, url)
            print(readability.title, len(readability.content))
            if len(readability.content)>20000:
                logging.debug("Got large content from %s .. trimming"%url)
                content = readability.content[:20000]
            else :
                content = readability.content
            store_doc(symbol, url,readability.title, content, new['date'])
        except Exception as e:
            print(e, new)

def store_doc(symbol,url, title, contents, date):
    conn = _get_doc_dbconn()
    cur = conn.cursor()
    cur.execute("INSERT INTO documents_document (url, title, content, symbol, date) VALUES (%s,%s, %s, %s,%s)",
                (url, title, contents, symbol, date))
    cur.close()
    conn.commit()

def main(args):
    conn = _get_dbconn()
    result = None
    if args.builddb:
        builddb(conn)
    if args.yahoo_news:
        result = get_yahoo_news(args.yahoo_news)
    if args.readability:
        readability(args.yahoo_news,result)
    #if args.instapaper_user:
    #    to_instapaper(result, args.instapaper_user, args.instapaper_pass)
    #if args.query:
    #result = query(conn, args.query)
    conn.close()
    return result

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename="stockdb.log")
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--builddb',   default=False, action="store_true",
                           help='build  database')
    parser.add_argument('--yahoo-news',   default='', help='show notification')
    parser.add_argument('--query',   default='', help='show notification')
    parser.add_argument('--readability', default=False, action="store_true", help='show notification')
    parser.add_argument('--instapaper-user',   default='stevenjose@gmail.com', help='show notification')
    parser.add_argument('--instapaper-pass',   default='fedoracore9', help='show notification')
    args = parser.parse_args()
    result = main(args)
    for result in result:
        print result
    sys.exit(0)
