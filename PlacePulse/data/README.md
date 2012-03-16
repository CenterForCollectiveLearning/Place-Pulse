Place Pulse Data
============
Old data from the previous version of Place Pulse. Pull it into mongo by running:

	mongoimport --host localhost -db placepulse --collection votes PlacePulse/data/votes_dump.json
	mongoimport --host localhost -db placepulse --collection studies PlacePulse/data/studies_dump.json
	mongoimport --host localhost -db placepulse --collection locations PlacePulse/data/locations_dump.json

dbrip.py
----------
The script used to generate the data dump is also included. You'll need MySQLdb for python installed, and a local mysql database named "placepulse".
