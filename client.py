from zmqrpc.client import ZMQRPC 
import sys
import pprint
import logging


rpc = ZMQRPC("tcp://127.0.0.1:5000",timeout=50000)
#rpc.builddb()
if not rpc.check_table_exists('indices'):
    rpc.build_indices_table()
if not rpc.check_table_exists('analytics'):
    rpc.build_analytics_table()
if not rpc.check_table_exists('stocks'):
    rpc.build_stock_table()
results = rpc.exec_tool('tools','ClientTools','week52diff',high_low='low')
print results

servers = rpc.__serverstatus__()
pprint.pprint(servers)
