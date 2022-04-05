import sys

import cx_Oracle
import os
from flask import Flask, render_template

app = Flask(__name__)

if sys.platform.startswith("darwin"):
    lib_dir = os.path.join(os.environ.get("HOME"), "Downloads", "instantclient_19_8")
    cx_Oracle.init_oracle_client(lib_dir=lib_dir)

connection = cx_Oracle.connect(user=os.environ.get("ORACLE_USER"),
                               password=os.environ.get("ORACLE_PASSWORD"),
                               dsn=os.environ.get("DATABASE_URL"))


@app.route('/')
def welcome(): # put application's code here
    cursor = connection.cursor
    return render_template("welcome.html",
                           cursor = cursor)


@app.route('/basic')
def basic():
    return render_template("basic_landing.html")


@app.route('/pro')
def pro():
    cursor = connection.cursor()
    cursor.execute("SELECT name, AVG(farm_income) income FROM commodity GROUP BY name")
    return render_template("pro_landing.html", cursor=cursor)


if __name__ == '__main__':
    app.run()
