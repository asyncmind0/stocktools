from zmqrpc.client import ZMQRPC 
import sys
import pprint
import logging


rpc = ZMQRPC("tcp://127.0.0.1:5000",timeout=50000)
rpc.builddb()
results = rpc.exec_tool('tools','ClientTools','week52diff',high_low='low')
print results

servers = rpc.__serverstatus__()
pprint.pprint(servers)
