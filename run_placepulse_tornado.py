from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from PlacePulse import app
import os
import sys

is_maintenance_mode = False
 
# Always throw a 503 during maintenance: http://is.gd/DksGDm
 
@app.before_request
def check_for_maintenance():
    if is_maintenance_mode:
        return 'Sorry, off for maintenance! We\'ll be back online in 10min', 503

if(len(sys.argv)!=2):
    print 'python run_placepulse_tornado.py #### \nwhere #### is port num'
    sys.exit(0)

http_server = HTTPServer(WSGIContainer(app))
port = int(sys.argv[1])
http_server.listen(port)
print 'Starting server instance on port: ', port
IOLoop.instance().start()
