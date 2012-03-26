from zmqrpc.client import ZMQRPC 
import sys
import pprint

rpc = ZMQRPC("tcp://127.0.0.1:5000",timeout=50000)
#rpc.builddb()
results= rpc.week52diff('low')

servers = rpc.__serverstatus__()
pprint.pprint(servers)
