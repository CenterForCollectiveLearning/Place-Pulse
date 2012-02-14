Place Pulse Data
============
Old data from the previous version of Place Pulse. Pull it into mongo by running:

    mongoimport -d placepulse -c locations_data data/mongo_dump.json 

dbrip.py
----------
The script used to generate the data dump is also included. You'll need MySQLdb for python installed, and a local mysql database named "placepulse".
