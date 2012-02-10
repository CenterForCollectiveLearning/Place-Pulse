Place Pulse
============
 To run Place Pulse on your local machine:
 Database Setup
 --------------------
 Download and install MongoDB from mongodb.org
 Open Terminal and type (without the $)
    $ sudo mkdir -p /data/db/
	$ sudo chown `id -u` /data/db
	$ cd /in/to/the/directory/where/you/installed/mongo
	$ cd ./bin
	$ ./mongod
		Fri Feb 10 12:01:22 [initandlisten] MongoDB starting : pid=8752 port=27017 dbpath=/data/db/ 64-bit host=your.hostname.whatever
		Fri Feb 10 12:01:22 [initandlisten] db version v2.0.2, pdfile version 4.5
		Fri Feb 10 12:01:22 [initandlisten] git version: 514b122d308928517f5841888ceaa4246a7f18e3
		Fri Feb 10 12:01:22 [initandlisten] build info: Darwin erh2.10gen.cc 9.6.0 Darwin Kernel Version 9.6.0: Mon Nov 24 17:37:00 PST 2008; root:xnu-1228.9.59~1/RELEASE_I386 i386 BOOST_LIB_VERSION=1_40
		Fri Feb 10 12:01:22 [initandlisten] options: {}
		Fri Feb 10 12:01:22 [initandlisten] journal dir=/data/db/journal
		Fri Feb 10 12:01:22 [initandlisten] recover : no journal files present, no recovery needed
		Fri Feb 10 12:01:22 [websvr] admin web console waiting for connections on port 28017
	
 Site Setup
 --------------------
 Clone Place-Pulse from GitHub git@github.com:philsalesses/Place-Pulse.git
 Open Terminal and type (without the $)
    $ cd /in/to/the/directory/you/just/cloned
	$ virtualenv ./ --distribute
		New python executable in ./bin/python
		Installing distribute...............done.
		Installing pip...............done.
	$ source setupEnv.sh
	$ pip install flask
		Installing flask...............done.
	$ pip freeze > requirements.txt
	$ python run_placepulse.py
    	* Running on http://localhost:8000/
    	* Restarting with reloader

And then, open up http://localhost:8000/ or http://localhost:8000/admin