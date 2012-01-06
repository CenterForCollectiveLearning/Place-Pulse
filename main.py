import os
import logging
from flask import Flask,render_template

app = Flask(__name__)

@app.route("/")
def main():
    return render_template('main.html')
    
@app.route("/study/create")
def create_study():
    return render_template('createstudy.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.logger.setLevel(logging.DEBUG)
    app.config.update(DEBUG=True,PROPAGATE_EXCEPTIONS=True,TESTING=True)
    app.run(debug=True,host='0.0.0.0',port=port)