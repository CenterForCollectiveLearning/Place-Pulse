Place Pulse
============
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