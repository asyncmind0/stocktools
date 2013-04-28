from debug import debug
import os
import sys
import time
import logging
import tornado.httpserver
import tornado.web
from tornado.options import options, define
from stormbase.options import configure
from stormbase.base_handler import get_static_handlers
from stormbase.session import SessionManager
from stormbase.database.couchdb import CouchDBAdapter
from stormbase.cache import MemcachedAdapter
from tornadotools.mongrel2.handler import Mongrel2Handler
from zmq.eventloop.minitornado.ioloop import IOLoop
#from zmq.eventloop.minitornado.ioloop import install as install_ioloop
from tornadotools.route import Route
from corduroy import Database

from handlers.home import HomeHandler
from handlers.portfolio import PortfolioHandler
import zerorpc
from threading import Thread


class StockApp(tornado.web.Application):
    def __init__(self, couchdb):
        self.db = couchdb
        handlers = Route.routes()
        handlers.extend(get_static_handlers())

        logging.info( "Added %s %s", len(handlers), " handlers.")
        logging.debug( "Hndlers: \n%s ", "\n".join([str(h) for h in handlers]))
        settings = dict(
            #static_path=os.path.join(os.path.dirname(__file__), '../static'),
            template_path=os.path.join(os.path.dirname(__file__), '../../html'),
            xsrf_cookies=True,
            cookie_secret=options.cookie_secret,
            session_secret=options.session_secret,
            memcached_addresses=options.memcached_addresses,
            session_timeout=1600,
            login_url="/authenticate",
            debug=options.debug,
            gzip=True,
            ui_modules={},
        )
        self.cache = MemcachedAdapter(options.memcached_addresses, binary=True)
        self.stockdb = zerorpc.Client("tcp://127.0.0.1:5000",timeout=50000)
        self.cache.flush_all()
        self.session_manager = SessionManager(
            options.session_secret,
            self.cache, options.session_timeout)
        super(StockApp, self).__init__(handlers, 'stockapp',
                                      **settings)

def extra_options():
    define("mongrel", default=False)
    define("admin_emails", type=list)
    define("site_title")
    define("site_description")

def main():
    try:
        extra_options()
        configure()
        if options.mongrel:
            # install the zmq version of the IOLoop
            ioloop = IOLoop.instance()
            ioloop.install()
        else:
            ioloop = tornado.ioloop.IOLoop.instance()
        db = Database('blog', (options.couchdb_user, options.couchdb_password))
        db = CouchDBAdapter(db)
        if not db:
            logging.error("Failed to connect to DB:%s", options.couchdb_database)
            sys.exit(1)
        if options.mongrel:
            handler = Mongrel2Handler(StockApp(db), "tcp://127.0.0.1:8000",
                                      "tcp://127.0.0.1:8001",
                                      no_keep_alive=True)
            handler.start()
        else:
            http_server = tornado.httpserver.HTTPServer(StockApp(db), xheaders=True)
            http_server.listen(options.port)
        logging.info(
            "Starting " + options.site_name + " @ port:" + str(options.port))
        sys.excepthook = debug
        ioloop.start()
        ipython_thread.join()
    except KeyboardInterrupt:
        logging.info("Exiting cleanly on KeyboardInterrupt")
    except Exception as e:
        logging.exception(e)
