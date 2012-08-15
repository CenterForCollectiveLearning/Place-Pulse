#!/usr/bin/python

import logging
import os

from flask import Flask

from PlacePulse import app

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.logger.setLevel(logging.DEBUG)
    app.config.update(DEBUG=True,PROPAGATE_EXCEPTIONS=True,TESTING=True)
    app.run(debug=True,host='0.0.0.0',port=port)