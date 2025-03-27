from flask import Flask, render_template
from tinydb import TinyDB, Query
import settings

app = Flask(__name__)

db = TinyDB('db.json')
db.insert(settings.PLC_CONFIGS)


@app.route("/")
def index():
    ip=-1
    token=-1
    motorschuetz=-1
    motorschutzschalter=-1
    return render_template("index.json", ip=ip, token=token, motorschuetz=motorschuetz, motorschutzschalter=motorschutzschalter)

if __name__ == "__main__":
    app.run()