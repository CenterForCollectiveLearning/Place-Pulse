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
	$ ./bin/mongod
	
Site Setup
--------------------
	
	Clone Place-Pulse from GitHub git@github.com:philsalesses/Place-Pulse.git
	Open Terminal and type (without the $)
	$ cd /in/to/the/directory/you/just/cloned
	$ virtualenv ./PlacePulse --distribute
	$ source setupEnv.sh
	$ pip install flask
	$ pip install pymongo
	$ pip install Flask-OAuth
	$ python ./run_placepulse.py
    	* Running on http://localhost:8000/
    	* Restarting with reloader

And then, open up http://localhost:8000/