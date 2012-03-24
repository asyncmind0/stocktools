# coding: utf-8
from debug import debug as sj_debug

import logging
import argparse
import sys
import sqlite3
import csv
import glob
from datetime import datetime, timedelta
from fish import ProgressFish, Bird, Fish, SwimFishNoSync
from analytics import get_name_sector


def get_num_lines():
    total_linenum = 0
    bird = Fish()
    for histfile in glob.glob("**/*.TXT"):
        with open(histfile) as f:
            for l in f:
                #bird.animate()
                total_linenum+= 1
    return total_linenum

def builddb(conn):
    print("Calculating data size")
    numlines = get_num_lines()
    print("Number of etries: %s"%numlines)
    fish = ProgressFish(total=numlines)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS stocks (sym text, date text, open real, close real, 
                    high real, low real, volume real, UNIQUE(sym,date) ON CONFLICT REPLACE)""")
    ptotal = 0
    for histfile in glob.glob("**/*.TXT"):
        with open(histfile, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                #print( row)
                #if i/1000:sys.stdout.write("\r%s of %s entries"%(numlines-i,  numlines))
                ptotal+=1
                #fish.animate(amount=ptotal)
                cur.execute(""" INSERT INTO stocks VALUES('%s',%s,%s, %s,%s,%s,%s)""" % (row[0],row[1],row[2],row[3],
                                row[4], row[5],row[6]))
    conn.commit()
    cur.close()

def query(conn,query):
    cur = conn.cursor()
    cur.execute("""SELECT * FROM stocks WHERE %s """%query)
    result = cur.fetchall()
    cur.close()
    return result

def all_symbols(conn):
    cur = conn.cursor()
    cur.execute("""SELECT DISTINCT sym FROM stocks """)
    result = cur.fetchall()
    cur.close()
    return result

def range_high_low(conn,symbol, start=None, end=None, high_low='high'):
    end = end or datetime.now()
    start = start or (end - timedelta(weeks=52))
    cur = conn.cursor()
    cur.execute("""SELECT %s, date FROM stocks WHERE
            sym='%s' and date BETWEEN %s AND %s""" \
                    %(high_low,symbol, start.strftime("%Y%m%d"), end.strftime("%Y%m%d")))
    result = cur.fetchall()
    cur.close()
    return result

def week52(conn, symbol, high_low='high'):
    result = range_high_low(conn,symbol,high_low=high_low)
    reverse  = False if high_low=='low' else True
    result.sort(key=lambda x:x[0], reverse=reverse)
    if not result:
        logging.debug("no 52week %s for %s" % (high_low,symbol))
    return result[0][0] if result else 0

def week52diff(conn, high_low='high'):
    symbols = map(lambda x:x[0], all_symbols(conn))
    w52highs = {}
    key = 'high'
    picks = []
    for sym in symbols:
        last_val = last_value(conn, sym, 'high')
        high52 = week52(conn,sym,'high')
        w52highs[sym] = {key:last_val,
             '52%s'%high_low:high52}
        change = last_val-high52 if high_low == 'low' else high52-last_val
        name, sector = get_name_sector(sym)
        picks.append((sym,change,high52, last_val, name, sector))
    reverse  = False if high_low=='low' else True
    picks.sort(key=lambda x:x[1],reverse=reverse)
    return picks

def last_value(conn, symbol, col):
    cur = conn.cursor()
    cur.execute("""SELECT %s,max(date) FROM stocks WHERE sym='%s' """%(col,symbol))
    result = cur.fetchall()
    cur.close()
    return result[0][0]

def main(args):
    conn = sqlite3.connect('asx.db')
    result = None
    if args.builddb:
        builddb(conn)
    if args.query:
        result = query(conn, args.query)
    if args.week52low:
        result = week52(conn, 'low')
    if args.week52high:
        result = week52(conn, 'high')
    if args.week52gainers:
        result = week52diff(conn,'high')
    if args.week52loosers:
        result = week52diff(conn,'low')
    if args.list_symbols:
        result = map(lambda x:x[0], all_symbols(conn))

    conn.close()
    return result



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename="stockdb.log")
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--builddb',   default=False, action="store_true",
                           help='build  database')
    parser.add_argument('--query',   default='', help='show notification')
    parser.add_argument('--week52high',   default='', help='show notification')
    parser.add_argument('--week52low',   default='', help='show notification')
    parser.add_argument('--week52gainers', default=False, action='store_true', help='show notification')
    parser.add_argument('--week52loosers', default=False, action='store_true', help='show notification')
    parser.add_argument('--list-symbols', default=False, action="store_true", help='build  database')
    args = parser.parse_args()
    result = main(args)
    print result
    sys.exit(0)

