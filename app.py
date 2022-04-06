import sys
import cx_Oracle
import os
import json
from flask import Flask, render_template, request, redirect, url_for

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
    return render_template("proform.html")


@app.route('/pro/<query_no>', methods=['GET', 'POST'])
def proform(query_no):
    path = "query" + query_no + "landing.html"
    if request.method == "POST":
        commodity = request.form.get('Commodity')
        return redirect(url_for('query_one', commodity=commodity))
    else:
        return render_template(path)


@app.route('/pro/1/<commodity>')
def query_one(commodity):
    sql = """
    SELECT name, farm_income, year
    FROM Commodity
    WHERE name = :commodity 
    """
    cursor = connection.cursor()
    cursor.execute(sql, commodity=commodity)
    return render_template("pro_landing.html", cursor=cursor)


if __name__ == '__main__':
    app.run()
