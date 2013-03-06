Place Pulse
===============
To run Place Pulse on a Mac using Homebrew:
If Homebrew is already installed, you can skip step 1 of the Database Setup.
If you prefer not to use Homebrew, install MongoDB using the intructions on their website and then pickup from step 2.

Database Setup
--------------------
    
    Open Terminal and type (without the $)
    $ ruby <(curl -fsSk https://raw.github.com/mxcl/homebrew/go)
	$ sudo mkdir -p /data/db/
	$ sudo chown `id -u` /data/db
	$ mongod
	
Site Setup
--------------------
	
	Clone Place-Pulse from GitHub git@github.com:philsalesses/Place-Pulse.git
	Open Terminal and type (without the $)
	$ cd /in/to/the/directory/you/just/cloned
	$ virtualenv ./PlacePulse --distribute
	$ source setupEnv.sh
	$ pip install -r requirements.txt
	$ python ./run_placepulse.py

Open up http://localhost:8000/

Deployment
--------------------

To deploy, you'll need to figure this out on your own depending on your setup. The code on GitHub was deployed using Tornado and WSGI. Now, for most projects, I (Phil Salesses) user Heroku and GUnicorn. For deployment instructions, contact phil.salesses@gmail.com for help.

License
===============
Place Pulse by Phil Salesses, Paul Sawaya, Michael Wong, Michael Xu, Deepak Jagdish and César Hidalgo is licensed under a Creative Commons Attribution 3.0 Unported License.

http://creativecommons.org/licenses/by/3.0/

Based on a work at http://pulse.media.mit.edu.