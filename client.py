from zmqrpc.client import ZMQRPC 
import sys
import pprint
import logging
import matplotlib.pyplot as plt
from datetime import datetime
import pylab
DATEFORMAT = "%Y%m%d"


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
#results = rpc.exec_tool('tools','ClientTools','week52diff',high_low='low')
#print results
servers = rpc.__serverstatus__()
pprint.pprint(servers)
