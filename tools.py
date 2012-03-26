import logging
class ClientTools(object):
    def __init__(self, rpc):
        self.rpc = rpc

    def week52(self, symbol, high_low='high'):
        result = self.rpc.date_range(symbol,columns=[high_low])
        result = filter(lambda x: x[0]>0,result)
        reverse  = False if high_low=='low' else True
        result.sort(key=lambda x:x[0], reverse=reverse)
        if not result:
            logging.debug("no 52week %s for %s" % (high_low,symbol))

        return result[0][0] if result else 0

    def week52diff(self, high_low='high'):
        symbols = map(lambda x:x[0], self.rpc.all_symbols())
        indices = self.rpc.get_indices()
        w52highs = {}
        key = 'high'
        picks = []
        for sym in symbols:
            if sym in indices:continue
            last_val = self.rpc.last_value(sym, 'high')
            high52 = self.week52(sym,'high')
            w52highs[sym] = {key:last_val,
                 '52%s'%high_low:high52}
            change = last_val-high52 if high_low == 'low' else high52-last_val
            name, sector = self.rpc.get_name_sector(sym)
            picks.append((sym,change,high52, last_val, name, sector))
        reverse  = False if high_low=='low' else True
        picks.sort(key=lambda x:x[1],reverse=reverse)
        return picks

