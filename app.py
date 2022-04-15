import sys
import cx_Oracle
import os
import json
from flask import Flask, render_template, request, redirect, url_for
from bokeh.plotting import figure
from bokeh.embed import components

app = Flask(__name__)

if sys.platform.startswith("darwin"):
    lib_dir = os.path.join(os.environ.get("HOME"), "Downloads", "instantclient_19_8")
elif sys.platform.startswith("linux"):
    lib_dir = "/opt/oracle/instantclient_21_5"
else:
    lib_dir = r"C:\Users\ayeja\Documents\Downloads\instantclient_21_3"

cx_Oracle.init_oracle_client(lib_dir=lib_dir)

connection = cx_Oracle.connect(user=os.environ.get("ORACLE_USER"),
                               password=os.environ.get("ORACLE_PASSWORD"),
                               dsn="oracle.cise.ufl.edu/orcl")


@app.route('/', methods=['GET', 'POST'])
def welcome():  # put application's code here
    value = 0
    if request.method == "POST":
        cursor = connection.cursor()
        sql = '''
        SELECT COUNT(*) FROM (
        SELECT name FROM Commodity
        UNION ALL
        SELECT name FROM Crop
        UNION ALL
        SELECT name FROM Livestock
        )
        '''
        cursor.execute(sql)
        value = cursor.fetchall()[0][0]
    return render_template("proform.html", value=value)


@app.route('/pro')
def pro():
    return render_template("proform.html")


@app.route('/pro/1', methods=['GET', 'POST'])
def query_one_form():
    if request.method == "POST":
        commodity = request.form.get('Commodity')
        return redirect(url_for('query_one', commodity=commodity))
    else:
        sql = """
        SELECT DISTINCT name
        FROM Commodity
        """
        cursor = connection.cursor()
        cursor.execute(sql)
        data = []
        for name in cursor.fetchall():
            data.append(name[0])
        return render_template("query1landing.html", data=data)


@app.route('/pro/1/<commodity>')
def query_one(commodity):
    sql = """
    SELECT name, year, SUM(farm_income) farm_income
    FROM Commodity
    WHERE name = :commodity
    GROUP BY name, year
    ORDER BY year, name ASC
    """
    cursor = connection.cursor()
    cursor.execute(sql, commodity=commodity)
    data = rows_to_dict_list(cursor)
    year = []
    farm_income = []
    for item in data:
        year.append(item['YEAR'])
        farm_income.append(item['FARM_INCOME'])
    print(year)
    print(farm_income)
    p = figure(title = "Cost Changes over Years", x_axis_label='Year', y_axis_label ='Price')
    p.line(year, farm_income, legend_label="Food ", color="blue", line_width=2)
    script, div = components(p)
    
    return render_template("query1results.html", bokehScript=script, bokehDiv=div)


def rows_to_dict_list(cursor):
    columns = [i[0] for i in cursor.description]
    return [dict(zip(columns, row)) for row in cursor]




if __name__ == '__main__':
    app.run()
