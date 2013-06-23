from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from PlacePulse import app
import os

# ONLY RUN THIS BEHIND A PROXY!
# Proxy Fixer needed for apache proxy in production, see http://flask.pocoo.org/docs/deploying/others/#proxy-setups

#from werkzeug.contrib.fixers import ProxyFix
#app.wsgi_app = ProxyFix(app.wsgi_app)

http_server = HTTPServer(WSGIContainer(app))
port = int(os.environ.get("PORT", 8000))
http_server.listen(port)
IOLoop.instance().start()