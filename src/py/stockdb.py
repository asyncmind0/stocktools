# coding: utf-8

import logging
import argparse
import sys,os 
import sqlite3
import csv
import glob
from datetime import datetime, timedelta
import ConfigParser, io
import zerorpc
import signal
import thread, threading
import sqlitebck
from tables import IsDescription,StringCol,Int64Col,UInt16Col,Float32Col,\
        Float64Col,Int32Col,Time32Col
from tables import openFile

DATEFORMAT = "%Y%m%d"
TIMEFORMAT = "%Y%m%d%H%M%S"
INMEMORY = True
DBFILE =":memory:" if INMEMORY else 'asx.db'
DATA_DIR = "../../data/"


def get_num_lines():
    total_linenum = 0
    for histfile in glob.glob("history/**/*.TXT"):
        with open(histfile) as f:
            for l in f:
                total_linenum+= 1
    return total_linenum

class Scrip(IsDescription):
    symbol = StringCol(5)
    date = Time32Col()
    open = Float32Col()
    close = Float32Col()
    high = Float32Col()
    low = Float32Col()
    volume = Int32Col()

class RpcObject(object):

    def exec_tool(self,toolpath,*args, **kwargs):
        toolmodule, toolset, toolname = toolpath.split('.')
        tools = __import__(toolmodule)
        tools = reload(tools)
        cl = getattr(tools,toolset)(self)
        #start = datetime.now()
        result =  getattr(cl,toolname)(*args, **kwargs)
        #print("Time taken for %s:%s" % (toolpath,(datetime.now()-start)))
        del cl
        del tools
        return result

    def get_status(self):
        return "Running"

    def shutdown(self):
        self._shutdown = True
        #return True
        os._exit(0)

class ScripTable(RpcObject):
    def __init__(self):
        self.h5file = openFile('stocktool.h5',mode='w',title='stocktool data file')
        self.group = self.h5file.createGroup('/','historical','historical stock data')
        self.historicaldata = self.h5file.createTable(
            self.group,'scrips',Scrip,'historical scrip')

    def load(self):
        start = datetime.now()
        print("Calculating historical stock data size")
        numlines = get_num_lines()
        print("Number of etries: %s"%numlines)
        ptotal = 0
        for histfile in glob.glob("history/ASX/**/*.TXT"):
            with open(histfile, 'r') as f:
                reader = csv.reader(f)
                trow = self.historicaldata.row
                for row in reader:
                    ptotal+=1
                    trow['symbol'] = row[0]
                    trow['date'] = int(row[1])
                    trow['open'] = float(row[2])
                    trow['close'] = float(row[3])
                    trow['high'] = float(row[4])
                    trow['low'] = float(row[5])
                    trow['volume'] = int(row[6])
                    trow.append()
                    #if ptotal%1000 ==0:
                    #    print '\r',
                    #    print ptotal,
        self.historicaldata.flush()
        print "Completed in %s "% (datetime.now()-start)


class StockDb(RpcObject):
    _conn = None
    _shutdown=False
    def __init__(self):
        self._conn = sqlite3.connect(DBFILE)
        with open("../sql/createtables.sql") as create:
            stmts = create.read().split(';')
            for i, s in enumerate(stmts):
                try:
                    cur = self._conn.cursor()
                    cur.execute(s)
                    cur.close()
                except Exception as e:
                    logging.debug("statement %s, %s", i, s)
                    logging.exception(e)
                    raise


    def get_status(self):
        return "Running"

    def get_name_sector(self,symbol):
        cur = self._conn.cursor()
        cur.execute("""SELECT name,sector FROM analytics WHERE sym='%s' """%symbol)
        result = cur.fetchall()
        cur.close()
        if not result:
            logging.debug("no info for %s"%symbol)
        return result[0] if result else ('','')

    def load_db(self,dbfile=os.path.join(DATA_DIR,'asx.db')):
        print("Loading db from from %s" % dbfile)
        bdb = sqlite3.connect(dbfile)
        sqlitebck.copy(bdb,self._conn)
        bdb.close()
        print("Loaded db from from %s" % dbfile)
        return True

    def dump_db(self,dbfile=os.path.join(DATA_DIR,'asx.db')):
        print("Dumping db to %s" % dbfile)
        bdb = sqlite3.connect(dbfile)
        sqlitebck.copy(self._conn,bdb)
        bdb.close()
        print("Dumped db to %s" % dbfile)
   

    def check_table_exists(self,table_name):
        cur = self._conn.cursor()
        cur.execute(
            """SELECT name FROM sqlite_master WHERE
            type='table' AND name='%s'"""%table_name)
        res = cur.fetchone()
        return True if res else False

    def build_indices_table(self):
        start = datetime.now()
        if not self.check_table_exists('fts'):
            self.build_fts()
        cur = self._conn.cursor()
        indices_file = os.path.join(DATA_DIR, 'ASXIndices.csv')
        with open(indices_file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                sym = row[1].strip()
                name = row[0].strip().replace("'","''")
                cur.execute(
                    """INSERT INTO indices VALUES('%s', '%s')""" % (sym, name))
                cur.execute("""INSERT INTO fts VALUES('%s', '%s')""" % (sym, name))
        self._conn.commit()
        cur.close()
        print "Completed Indices in %s "% (datetime.now()-start)

    def build_analytics_table(self):
        start = datetime.now()
        if not self.check_table_exists('fts'):
            self.build_fts()
        cur = self._conn.cursor()
        ptotal = 0
        symbol_map = os.path.join(DATA_DIR, 'ASXListedCompanies.csv')
        with open(symbol_map, 'r') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i==1:continue
                sym = row[1].strip()
                name = row[0].strip().replace("'","''")
                sector = row[2].strip().replace("'","''")
                week52high = 0
                week52low = 0
                last_price = 0
                cur.execute(
                    """ INSERT INTO analytics VALUES('%s','%s','%s', %s,%s,%s)"""
                % (sym,name,sector,week52high,week52low,last_price))
                cur.execute("""INSERT INTO fts VALUES('%s', '%s')""" % (sym,name))
        self._conn.commit()
        cur.close()
        print "Completed Analytics in %s "% (datetime.now()-start)

    def build_stock_table(self):
        start = datetime.now()
        print("Calculating historical stock data size")
        numlines = get_num_lines()
        print("Number of etries: %s"%numlines)
        cur = self._conn.cursor()
        ptotal = 0
        for histfile in glob.glob(os.path.join(DATA_DIR, "**/*.TXT")):
            with open(histfile, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    #print( row)
                    #if i/1000:sys.stdout.write(
                    #"\r%s of %s entries"%(numlines-i,  numlines))
                    ptotal+=1
                    cur.execute(
                        """ INSERT INTO stocks VALUES('%s',%s,%s, %s,%s,%s,%s)"""
                        % tuple(row[:7]))
                    #if ptotal%1000 ==0:
                    #    print '\r',
                    #    print ptotal,
        self._conn.commit()
        cur.close()
        print "Completed in %s "% (datetime.now()-start)


    def build_fts(self):
        return
        cur = self._conn.cursor()
        cur.execute("""""")
        self._conn.commit()
        cur.close()


    def query(self,query):
        cur = self._conn.cursor()
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
        cur = self._conn.cursor()
        cur.execute("""SELECT DISTINCT sym FROM stocks """)
        result = cur.fetchall()
        cur.close()
        return map(lambda x:x[0],result) if result else []

    def get_indices(self):
        cur = self._conn.cursor()
        cur.execute("""SELECT DISTINCT sym FROM indices """)
        result = cur.fetchall()
        cur.close()
        return map(lambda x:x[0],result)

    def date_range(self,symbol, start=None, end=None, columns=['high']):
        end = end or datetime.now()
        start = start or (end - timedelta(weeks=52))
        cur = self._conn.cursor()
        scolumns = ''
        for column in columns:
            scolumns+='%s, '
        params = tuple(scolumns, columns+[symbol,start.strftime("%Y%m%d"),
                                          end.strftime("%Y%m%d")])
        cur.execute(
            """SELECT %s date FROM stocks WHERE sym='%s'
            and date BETWEEN %s AND %s""" , *params)
        result = cur.fetchall()
        cur.close()
        return result

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
    logging.basicConfig(level=logging.DEBUG)#, filename="stockdb.log")
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--builddb',   default=False, action="store_true",
                           help='build  database')
    parser.add_argument('--query',   default='', help='show notification')
    parser.add_argument('--week52high',   default='', help='show notification')
    parser.add_argument('--week52low',   default='', help='show notification')
    parser.add_argument('--week52gainers', default=False, action='store_true',
                        help='show notification')
    parser.add_argument('--week52loosers', default=False, action='store_true',
                        help='show notification')
    parser.add_argument('--list-symbols', default=False, action="store_true",
                        help='build  database')
    args = parser.parse_args()
    def signal_handler(signal, frame):
        print 'You pressed Ctrl+C!'
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    server = zerorpc.Server(StockDb())
    #server = ZMQRPCServer(ScripTable)
    server.bind('tcp://0.0.0.0:5000')
    print("Starting RPC server")
    server.run()
    print "Done"
    sys.exit(0)

