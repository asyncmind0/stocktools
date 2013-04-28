import re
import markdown
import unicodedata
from diff_match_patch import diff_match_patch as Dmp
from datetime import datetime
from tornado import gen, web
from tornadotools.route import Routes
from stormbase.base_handler import async_engine
from stormbase.asyncouch.couchversions import Diff
from stormbase.jinja import format_datetime
from stocktools.handlers.base import BaseHandler
from stocktools.models import User
from uuid import uuid4

class ValidationError(Exception):
    pass

class Portfolio(object):
    def __init__(self, stockdb):
        self.stockdb = stockdb
    def _validate_sym(self, sym):
        return sym.upper()

    def _add_trade(self, raw_data):
        data = []
        errors = []
        for field in ['sym', 'cost', 'date', 'quantity', 'fee']:
            try:
                validator = getattr(self, '_validate_%s' % field, None) \
                            or (lambda x: x)
                data.append(validator(raw_data[field]))
            except ValidationError as e:
                errors.append(e)
        if errors:
            raise errors
        portfolio = self.stockdb.exec_tool(
            'tools.Portfolio.add', *data)

@Routes((r'/symboldata', dict(render_method='json')),)
class SymbolDataHandler(BaseHandler):
    def get(self):
        symbols = self.application.stockdb.exec_tool(
                'tools.ClientTools.all_symbols_names_sectors', None)
        self.end(identifier='sym',
                      label='name',
                      items=[dict(sym=r[0], name=r[1], sector=r[2])
                             for r in symbols])
                      
@Routes((r'/portfoliodata', dict(render_method='json')),)
class PortfolioDataHandler(BaseHandler):
    def get(self):
        self.user = None
        portfolio_data = self.application.stockdb.exec_tool(
            'tools.Portfolio.get', self.user)

        symbols = [p[0] for p in portfolio_data]
        self.quotes = self.application.stockdb.exec_tool(
            'tools.ClientTools.get_history', symbols)
        self.prices = dict(self.application.stockdb.exec_tool(
            'tools.ClientTools.get_prices', symbols, 'close', None))
        symbols = self.application.stockdb.exec_tool(
            'tools.ClientTools.all_symbols_names_sectors',
            'where sym in (%s)' % ','.join([ "'%s'" % s for s in symbols]))
        symbol_map = {s[0]: s[1:] for s in symbols}
        def number(val):
            return val if val else 0
        portfolios = ['portfolio1', 'portfolio2', 'portfolio3']
        itemx3 =[]
        for x in range(0,3):
            items = [dict(id=str(uuid4()),
                      sym=r[0], cost=r[1], date=r[2], quantity=r[3],
                          price=number(number(self.prices[r[0].upper()])*float(r[3])),
                          name=symbol_map.get(r[0], [''])[0],
                          sector=symbol_map.get(r[0], ['',''])[1],
                      fee=r[4])
                 for r in portfolio_data]
            itemx3.append(dict(portfolio='portfolio%s'%x, id=str(uuid4()),
                               price=sum([x['price'] for x in items]),
                               cost=sum([x['cost'] for x in items]),
                               quantity=sum([x['quantity'] for x in items]),
                               fee=sum([x['fee'] for x in items]),
                               children=items))
            #itemx3.extend(items)
        self.end(identifier='id',
                 items=itemx3)
            

@Routes((r'/portfolio/*([^/]*)'),)
class PortfolioHandler(BaseHandler):
    template = 'base'
    quotes = {}
    def block_content(self):
        return self.render_engine.renderer.render_name(
            "portfolio", self)
        
    def _get_price(self, sym, date):
        return dict(self.application.stockdb.exec_tool(
                'tools.ClientTools.get_prices', sym, 'close', date))
    @async_engine
    def get(self, method, *args, **kwargs):
        print "in"
        template = "base"
        self.user = 'sjoseph'
        if self.get_argument('result', None) == '0':
            self.response = "added"
        if method == 'get_price':
            self.render_method = 'json'
            self.end(sym=self._get_price(
                self.get_argument('sym'),
                self.get_argument('date', None)))
        elif method == 'add_trade':
            self.template = "trade"
            self.end()
        else:
            self.end()

    @async_engine
    def post(self, action):
        portfolio = Portfolio(self.application.stockdb)
        result = "Failed"
        if action == 'add':
            result = portfolio._add_trade(self.query_dict)
        self.redirect('/portfolio/?result=0')
        pass
