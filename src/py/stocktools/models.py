import dateutil
import dateutil.parser
from datetime import datetime
from stormbase.util import tuct
from stormbase.database.couchdb import BaseDocument


class User(BaseDocument):
    """Base User objext
    """
    defaults = tuct(
        first_name="",
        last_name="",
        email="",
        entries=[],
        comments=[],
        facebook_id=0,
        twitter_id="",
        friendfeed_id="",
        linkedin_id="",
        linkedin_headline="",
        linkedin_profile="",
        openid="",
        invitee=[],
        photo='',
        profile="",
        created=str(datetime.utcnow()))

    def get_formatted_name(self):
        return "%s %s" % (self.first_name, self.last_name)

