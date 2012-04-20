import logging
import sys
from datetime import datetime
import numpy as np
class AlphaTools(object):
    def __init__(self, rpc):
        self.rpc = rpc
    def get_price(self,symbol, columns=['close']):
        table = self.rpc.h5file.root.historical.scrips
        columns.insert(0,'date')
        #price = max([(x['close'],x['date']) for x in \
                #        table.where("symbol == '%s'"%symbol)],key=lambda x:x[1])
        price = max(map(lambda x: [x[key] for key in columns],
            table.where("symbol == '%s'"%symbol)),key=lambda x:x[0])
        #price  = max(table.where("symbol == '%s'"%symbol),key=lambda x:x['close'])
        #return price['close']
        return price

class ClientTools(object):
    def __init__(self, rpc):
        self.rpc = rpc

    def test_rpc(self, arg1,arg2, kwarg1='kwarg1', kwarg2='kwarg2'):
        print 'arg1=%s' %arg1
        print 'arg2=%s' %arg2
        print 'kwarg1=%s' %kwarg1
        print 'kwarg2=%s' %kwarg2

    def last_value(self, symbol, col):
        cur = self.rpc.conn.cursor()
        cur.execute("""SELECT %s,max(date) FROM stocks WHERE sym='%s' """%(col,symbol))
        result = cur.fetchall()
        cur.close()
        return result[0][0]

    def week52(self, symbol, high_low='high'):
        """
            Definition of '52-Week Range' The lowest and highest prices
            at which a stock has traded in the previous 52 weeks. The
            52-week range is provided in a stock's quote summary along
            with information such as today's change and year-to-date
            change. Companies that have been trading for less than a
            year will still show a 52-week range even though there isn't
            data for the full range.

            Investopedia explains '52-Week Range' Technical analysts
            compare a stock's current trading price to its 52-week range
            to get a broad sense of how the stock is doing, as well as
            how much the stock's price has fluctuated. This information
            may indicate the potential future range of the stock and how
            volatile the shares are.

            Read more:
                http://www.investopedia.com/terms/1/52-week-range.asp#ixzz1qHFs5uqw
        """
        result = self.rpc.date_range(symbol,columns=[high_low])
        result = filter(lambda x: x[0]>0,result)
        reverse  = False if high_low=='low' else True
        result.sort(key=lambda x:x[0], reverse=reverse)
        if not result:
            logging.debug("no 52week %s for %s" % (high_low,symbol))

        return result[0][0] if result else -1

    def week52diff(self, high_low='high'):
        """
            Definition of '52-Week High/Low' The highest and lowest
            price at which a stock has traded in the past 12 months, or
            52 weeks.

            Many investors see the 52-week high or low as an important
            indicator. For example, a value investor may view a stock
            trading at a 52-week low as an initial indication of a
            possible value play (a stock sitting at a price below its
                    intrinsic value). An astute value investor will have
            to conduct a lot more analysis to come to this conclusion,
            but the fact that the stock is trading at its 52-week low
            can be a potential starting point.

            Read more:
                http://www.investopedia.com/terms/1/52weekhighlow.asp#ixzz1qHFg9nQv
        """
        symbols =  self.rpc.all_symbols()
        print "SYMBOLS:%s"% len(symbols)
        indices = self.rpc.get_indices()
        w52highs = {}
        key = 'high'
        picks = []
        for sym in symbols:
            if sym in indices:continue
            high52 = self.week52(sym,'high')
            if high52 <0:
                continue
            last_val = self.last_value(sym, 'high')
            w52highs[sym] = {key:last_val,
                 '52%s'%high_low:high52}
            change = last_val-high52 if high_low == 'low' else high52-last_val
            name, sector = self.rpc.get_name_sector(sym)
            picks.append((sym,change,high52, last_val, name, sector))
        reverse  = False if high_low=='low' else True
        picks.sort(key=lambda x:x[1],reverse=reverse)
        return picks

    def relative_strength(self, symbol):
        """
            A technical momentum indicator that compares the magnitude
            of recent gains to recent losses in an attempt to determine
            overbought and oversold conditions of an asset. It is
            calculated using the following formula:

                RSI = 100 - 100/(1 + RS*)

                *Where RS = Average of x days' up closes / Average of x
                days' down closes.

            An asset is deemed to be overbought once the RSI approaches
            the 70 level, meaning that it may be getting overvalued and
            is a good candidate for a pullback. Likewise, if the RSI
            approaches 30, it is an indication that the asset may be
            getting oversold and therefore likely to become undervalued.
            A trader using RSI should be aware that large surges and
            drops in the price of an asset will affect the RSI by
            creating false buy or sell signals. The RSI is best used as
            a valuable complement to other stock-picking tools.

            Read more:
                http://www.investopedia.com/terms/r/rsi.asp#ixzz1qHEncj8m
        """
        result = self.rpc.date_range(symbol,columns=['close'])
        up_close = []
        down_close = []
        prevres = 0
        for res in result:
            if res[0] > prevres:
                up_close.append(res[0])
            elif res[0] < prevres:
                down_close.append(res[0])
            prevres = res

        avg_up = np.average(up_close)
        print 'avg_up = %s' % avg_up
        avg_down = np.average(down_close)
        print 'avg_down = %s' % avg_down
        rsi = 100-100/(1+ (avg_up /avg_down))
        return rsi

    def get_sectors(self ):
        cur = self.rpc.conn.cursor()
        cur.execute("""SELECT DISTINCT(sector) FROM analytics""")
        result = cur.fetchall()
        cur.close()
        return map(lambda x:x[0],result) if result else []

    def get_sector_stocks(self,sector):
        cur = self.rpc.conn.cursor()
        cur.execute("""SELECT DISTINCT(sym),name FROM analytics WHERE sector = '%s'"""%sector)
        result = cur.fetchall()
        cur.close()
        return result
        #return map(lambda x:x[0],result) if result else []

    def get_sector_leaders2(self, sector):
        cur = self.rpc.conn.cursor()
        query1 = """SELECT stocks.close,stocks.volume,
                    stocks.sym,stocks.date,analytics.name 
                    FROM stocks LEFT OUTER JOIN analytics ON analytics.sym = stocks.sym
                    WHERE analytics.sector = '%s'
                    and stocks.sym in (select """ % sector
        query2 = """SELECT max(stocks.date),sym from stocks group by sym"""
        query3 = """SELECT stocks.close,stocks.volume,stocks.sym,max(stocks.date), analytics.name 
                    from stocks,analytics where stocks.sym = analytics.sym and analytics.sector ='%s' 
                    group by stocks.sym""" % sector
        cur.execute(query3)
        result = cur.fetchall()
        result.sort(key=lambda x:x[0], reverse=True)
        return result

    def get_sector_leaders(self, sector):
        cur = self.rpc.conn.cursor()
        sector_stocks = self.get_sector_stocks(sector)
        sector_prices = []
        for sym in sector_stocks:
            cur.execute("""SELECT stocks.close,stocks.volume,
                    stocks.sym,max(stocks.date),analytics.name 
                    FROM stocks, analytics 
                    WHERE stocks.sym = '%s' and analytics.sym = '%s' and analytics.sector = '%s' """ % \
                            (sym[0], sym[0], sector))
            sector_prices.append(cur.fetchone())
        cur.close()
        sector_prices.sort(key=lambda x:x[0], reverse=True)
        return sector_prices

    def search(self,term):
        cur = self.rpc.conn.cursor()
        cur.execute("""SELECT * FROM fts WHERE name MATCH '%s'""" % term)
        result = cur.fetchall()
        cur.close()
        return result

    def get_prices(self,stocks, column):
        stocks = stocks.split(',') if isinstance(stocks,(str,unicode)) else []
        prices = []
        for stock in stocks:
            prices.append((stock,self.rpc.last_value(stock,column)))
        return prices

    def simple_moving_average(self, symbol, n=5):
        cur = self.rpc.conn.cursor()
        #maN = 'ma%s' % n
        #prev_maN = None
        #try:
        #    cur.execute("""SELECT %s, max(date) FROM stocks WHERE sym ='%s'""" % (maN, symbol))
        #    prev_maN = cur.fetchone()
        #    prev_maN = prev_maN[0][0]
        #except Exception as e:
        #    prev_maN = None
        #    pass
        cur.execute("""SELECT close,date FROM stocks WHERE sym ='%s'""" % ( symbol))
        result = cur.fetchall()
        prices = map(lambda x:x[0], result)
        #maN = 
        #every day take the previous 5 days values and get average
        sma = [0]*len(prices)
        sma = [sum(prices[:n])/n]*len(prices)
        for i, close in enumerate(prices,0):
            if i<=5:continue
            #sma[i]=sma[i-1]-((prices[i-n-1]/n)+(prices[i]/n))
            sma[i] = sum(prices[i-n:i])/n
        return zip(sma, prices, map(lambda x:x[1],result))



        cur.close()

    def all_symbols_names_sectors(self):
        cur = self.rpc.conn.cursor()
        cur.execute("""SELECT sym,name,sector FROM analytics ORDER BY sym""")
        result = cur.fetchall()
        cur.close()
        return result
    def get_info(self, symbol):
        cur = self.rpc.conn.cursor()
        cur.execute("""SELECT sym,name,sector FROM analytics 
                WHERE sym = '%s' ORDER BY sym""" % symbol)
        result = cur.fetchone()
        cur.close()
        return result
