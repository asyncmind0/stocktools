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

@Routes((r'/'))
class HomeHandler(BaseHandler):
    template = 'base'
    quotes = {}
    portfolio = {}
    def block_content(self):
        return self.render_engine.renderer.render_name(
            "home", self)

    @async_engine
    def get(self, *args, **kwargs):
        print "in"
        template = "base"
        user = 'sjoseph'
        self.end()

    @async_engine
    def post(self, action):
        result = "Failed"
        if action == 'add':
            result = self._add_trade()
        self.redirect('/?result=0')
        pass
