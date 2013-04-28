import re
import markdown
import unicodedata
from datetime import datetime
from tornado import stack_context
from tornado import gen, web
from stormbase.base_handler import async_engine
from stormbase.base_handler import StormBaseHandler
from stormbase.asyncouch.couchversions import Diff
from tornadotools.route import Routes
from diff_match_patch import diff_match_patch as Dmp
from stormbase.debug import set_except_hook
from stocktools.models import User


class BaseHandler(StormBaseHandler):
    iconset = "fc-webicon"

    def get_current_user(self):
        userid = self.get_secure_cookie("user")
        user_obj = None
        if self.session:
            user_obj = self.session.get(userid, None)
        # logging.debug("LOGINSTATUS: %s, %s" % (userid, user_obj is not None))
        if not userid or not user_obj:
            return None
        return User(user_obj)

    def initialize(self, *args, **kwargs):
        kwargs['render_engine'] = "mustache"
        set_except_hook()
        super(BaseHandler, self).initialize(args, **kwargs)

    def user_name(self):
        return self.current_user.first_name if self.current_user else ""
    
