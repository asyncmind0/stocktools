from zmqrpc.client import ZMQRPC
import sys
import pprint
import logging
import matplotlib.pyplot as plt
from datetime import datetime
import pylab
import urllib2
import json
from dateutil.parser import parse as dateparse
DATEFORMAT = "%Y%m%d"
TIMEFORMAT = "%Y%m%d"
YAHOO_API="http://query.yahooapis.com/v1/public/yql?q=%s&format=json"
GOOGLE_API="http://finance.google.com/finance/info?client=ig&q=%s"


def plot_stock_graph(rpc, symbol, startdate=None, enddate=None):
    hist = rpc.date_range(symbol)
    avg = map(lambda x:x[0],hist)
    dates = map(lambda x: datetime.strptime(str(x[1]),DATEFORMAT),hist)
    #http://www.gossamer-threads.com/lists/python/python/665196
    pylab.plot_date(pylab.date2num(dates), avg,linestyle='-', marker='None')

rpc = ZMQRPC("tcp://127.0.0.1:5000",timeout=50000)
print "Server is %s" % rpc.get_status()
if len(sys.argv)>1:
    method = getattr(rpc,sys.argv[1])
    result = method()

def init_tables(rpc):
    if not rpc.check_table_exists('indices'):
        rpc.build_indices_table()
    if not rpc.check_table_exists('analytics'):
        rpc.build_analytics_table()
    if not rpc.check_table_exists('stocks'):
        rpc.build_stock_table()

def get_yahoo_news(symbol):
    yqlquery = """select * from html where url="http://finance.yahoo.com/q?s=%s" and xpath='//div[@id="yfi_headlines"]/div[2]/ul/li' """% symbol
    print yqlquery
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
def get_price_google(symbol):
    googlequery = GOOGLE_API % urllib2.quote('ASX:'+symbol)
    results = urllib2.urlopen(googlequery).read()
    results = json.loads(results[3:])
    return results

#results = rpc.exec_tool('tools','ClientTools','week52diff',high_low='low')
#print results
servers = rpc.__serverstatus__()
pprint.pprint(servers)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

def print_portfolios():
    from termcolor import colored
    from table import pprint_table
    from portfolios import portfolios
    import ystockquote

    header = []

    for h in ["SYM","MKT PRICE", "MKT VALUE", "PUR PRICE", "PUR VALUE", "CHANGE", "TOTAL_CHG"]:
        header.append(colored(h,'magenta'))

    myscrips = [
        header,]

    def colorize(val):
        return colored(str(val),'red' if val<0 else 'green')

    portfolio_mkt_val = 0
    portfolio_pur_val = 0

    for name,portfolio in portfolios.items():
        print colored(name,'cyan')
        print "="*80
        for scrip in portfolio:
            script_details = ystockquote.get_all(scrip['sym'])
            scrip_price = float(script_details['price'])
            portfolio_mkt_val+=scrip_price*scrip['qty']
            portfolio_pur_val+=scrip['value']*scrip['qty']
            myscrips.append([
                    colored(str(scrip['sym']),'white'),
                    colored(str(scrip_price),'white'),
                    colored(str(scrip_price*scrip['qty']),'white'),
                    colored(str(scrip['value']),'white'),
                    colored(str(scrip['value']*scrip['qty']),'white'),
                    colorize(scrip_price-scrip['value']),
                    colorize((scrip_price*scrip['qty'])-(scrip['value']*scrip['qty']))])

        pprint_table(myscrips)
        print "Portfolio: %s (mkt) %s (pur)" % (portfolio_mkt_val,portfolio_pur_val)
        print "Gain: %s " % colorize(portfolio_mkt_val-portfolio_pur_val)
