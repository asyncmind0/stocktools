# coding: utf-8
from debug import debug as sj_debug

import logging
import argparse
import sys
import sqlite3
import csv
import glob
from datetime import datetime, timedelta
from analytics import get_name_sector
import ConfigParser, io
from zmqrpc.server import ZMQRPCServer, LISTEN, CONNECT
DATEFORMAT = "%Y%m%d"
TIMEFORMAT = "%Y%m%d%H%M%S"
INMEMORY = False
DBFILE ='asx.db' if not INMEMORY else ":memory:"

class StockTool(object):
    conn = None
    def __init__(self):
        self.conn = sqlite3.connect(DBFILE)
        print self.check_lastupdate(update=True)
        print self.check_lastupdate()

    def get_num_lines(self):
        total_linenum = 0
        for histfile in glob.glob("history/**/*.TXT"):
            with open(histfile) as f:
                for l in f:
                    total_linenum+= 1
        return total_linenum

    def builddb(self):
        start = datetime.now()
        print("Calculating data size")
        numlines = self.get_num_lines()
        print("Number of etries: %s"%numlines)
        cur = self.conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS stocks (sym text, date text, open real, close real,
                        high real, low real, volume real, UNIQUE(sym,date) ON CONFLICT REPLACE)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS indices (sym text, name text,
                         UNIQUE(sym) ON CONFLICT REPLACE)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS analytics (sym text, name text, sector text, week52high real,
                        week52low real, last_price real, UNIQUE(sym) ON CONFLICT REPLACE)""")
        ptotal = 0
        symbol_map = 'ASXListedCompanies.csv'
        with open(symbol_map, 'r') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i==1:continue
                cur.execute(""" INSERT INTO analytics VALUES('%s','%s','%s', %s,%s,%s)""" \
                    % (row[1],row[0].replace("'","''"),row[2],0, 0,int(datetime.now().strftime(DATEFORMAT))))

        ptotal = 0
        for histfile in glob.glob("history/**/*.TXT"):
            with open(histfile, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    #print( row)
                    #if i/1000:sys.stdout.write("\r%s of %s entries"%(numlines-i,  numlines))
                    ptotal+=1
                    cur.execute(""" INSERT INTO stocks VALUES('%s',%s,%s, %s,%s,%s,%s)""" % (row[0],row[1],row[2],row[3],
                                    row[4], row[5],row[6]))
                    if ptotal%1000 ==0:
                        print '\r',
                        print ptotal,
        indices_file = 'ASXIndices.csv'
        with open(indices_file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                cur.execute("""INSERT INTO indices VALUES('%s', '%s')""" % (row[1].strip(),row[0].strip()))
        self.conn.commit()
        cur.close()
        print "Completed in %s "% (datetime.now()-start)

    def query(self,query):
        cur = self.conn.cursor()
        cur.execute("""SELECT * FROM stocks WHERE %s """%query)
        result = cur.fetchall()
        cur.close()
        return result

    def check_lastupdate(self,update=False):
        config = Config.get_config()
        result = 0
        now = int(datetime.now().strftime(TIMEFORMAT))
        if update:
            config.set('week52lastupdate', str(now))
            config.write()
        else:
            now -  int(config.get('week52lastupdate'))
        return result

    def all_symbols(self):
        cur = self.conn.cursor()
        cur.execute("""SELECT DISTINCT sym FROM stocks """)
        result = cur.fetchall()
        cur.close()
        return result

    def get_indices(self):
        cur = self.conn.cursor()
        cur.execute("""SELECT DISTINCT sym FROM indices """)
        result = cur.fetchall()
        cur.close()
        return map(lambda x:x[0],result)

    def range_high_low(self,symbol, start=None, end=None, high_low='high'):
        end = end or datetime.now()
        start = start or (end - timedelta(weeks=52))
        cur = self.conn.cursor()
        cur.execute("""SELECT %s, date FROM stocks WHERE
                sym='%s' and date BETWEEN %s AND %s""" \
                        %(high_low,symbol, start.strftime("%Y%m%d"), end.strftime("%Y%m%d")))
        result = cur.fetchall()
        cur.close()
        return result

    def week52(self, symbol, high_low='high'):
        result = self.range_high_low(symbol,high_low=high_low)
        reverse  = False if high_low=='low' else True
        result.sort(key=lambda x:x[0], reverse=reverse)
        if not result:
            logging.debug("no 52week %s for %s" % (high_low,symbol))
        return result[0][0] if result else 0

    def week52diff(self, high_low='high'):
        symbols = map(lambda x:x[0], self.all_symbols())
        indices = self.get_indices()
        w52highs = {}
        key = 'high'
        picks = []
        for sym in symbols:
            if sym in indices:continue
            last_val = self.last_value(sym, 'high')
            high52 = self.week52(sym,'high')
            w52highs[sym] = {key:last_val,
                 '52%s'%high_low:high52}
            change = last_val-high52 if high_low == 'low' else high52-last_val
            name, sector = get_name_sector(sym)
            picks.append((sym,change,high52, last_val, name, sector))
        reverse  = False if high_low=='low' else True
        picks.sort(key=lambda x:x[1],reverse=reverse)
        return picks

    def last_value(self, symbol, col):
        cur = self.conn.cursor()
        cur.execute("""SELECT %s,max(date) FROM stocks WHERE sym='%s' """%(col,symbol))
        result = cur.fetchall()
        cur.close()
        return result[0][0]

    def main(args):
        conn = sqlite3.connect(DBFILE)
        print check_lastupdate(update=True)
        print check_lastupdate()
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

class Config(object):
    defaultconfig = None
    def __init__(self):
        self.config = ConfigParser.SafeConfigParser()
        self.config.add_section('stocktool')
        self.config.set('stocktool','week52lastupdate','0')
        self.config.set('stocktool','stock_lastupdate','0')

        with open('stocktool.cfg','r') as cf:
            self.config.read(cf)

    def set(self,attr, value):
        self.config.set('stocktool',attr,value)

    def get(self,attr):
        return self.config.get('stocktool', attr)


    def write(self):
        with open('stocktool.cfg','w') as cf:
            self.config.write(cf)

    @classmethod
    def get_config(cls):
        if not cls.defaultconfig:
            cls.defaultconfig = Config()
        return cls.defaultconfig


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
    server = ZMQRPCServer(StockTool)
    server.queue('tcp://0.0.0.0:5000',thread=True)
    server.work(workers=1)
    #result = main(args)
    #print(result)
    sys.exit(0)

