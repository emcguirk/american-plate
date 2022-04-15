import sys
import cx_Oracle
import os
import json
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

if sys.platform.startswith("darwin"):
    lib_dir = os.path.join(os.environ.get("HOME"), "Downloads", "instantclient_19_8")
elif sys.platform.startswith("linux"):
    lib_dir = "/opt/oracle/instantclient_21_5"
else:
    lib_dir = os.path.join(os.environ.get("USERPROFILE"), "OneDrive", "Downloads", "instantclient_19_8")

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
        return redirect(url_for('query_one_results', commodity=commodity))
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
def query_one_results(commodity):
    sql = """
    SELECT name, year, SUM(farm_income)
    FROM Commodity
    WHERE name = :commodity
    GROUP BY name, year
    """
    cursor = connection.cursor()
    cursor.execute(sql, commodity=commodity)
    data = rows_to_dict_list(cursor)
    return render_template("query1results.html", data=data)


@app.route('/pro/2/<animal>/<vegetable>')
def query_two_results(animal, vegetable):
    sql = """
        SELECT cr_year year, animal_income/veg_income FROM
        (SELECT c.year ls_year, ls.name animal_name, sum(farm_income) animal_income
        from Commodity c JOIN Livestock ls
        ON c.name = ls.name
        WHERE ls.name = :animal
        group by c.year, ls.name) animal
        JOIN
        (SELECT cr.year cr_year, cr.name veg_name, sum(farm_income) veg_income
        FROM Commodity c JOIN Crop cr
        ON cr.name = c.name
        where cr.name = :vegetable
        group by cr.year, cr.name) veg
        ON ls_year = cr_year
        """
    cursor = connection.cursor()
    cursor.execute(sql, animal=animal, vegetable=vegetable)
    data = rows_to_dict_list(cursor)
    return render_template("query2results.html", data=data)


@app.route('/pro/3/<crop>')
def query_three_results(crop):
    sql = """
    SELECT c.region, cr.year, SUM(acres_harvested)
    FROM Commodity c
    JOIN
    CROP cr ON cr.State = c.State
    WHERE cr.name = :crop
    GROUP BY c.region, cr.year
    """
    cursor = connection.cursor()
    cursor.execute(sql, crop=crop)
    data = rows_to_dict_list(cursor)
    return render_template("query3results.html", data=data)


@app.route('/pro/4/<state>/<county>')
def query_four_results(state, county):
    sql = '''
    SELECT income.year, income.earnings/value.assets ROI FROM
    (SELECT year, SUM(farm_income) earnings
    FROM Commodity
    WHERE state = :state AND county = :county
    GROUP BY year) income
    JOIN
    (SELECT year, sum(asset_value) assets
    FROM Land_Value
    WHERE state = :state AND county = :county
    GROUP BY year) value
    ON income.year = value.year
    '''
    state = state.upper()
    county = county.upper()
    cursor = connection.cursor()
    cursor.execute(sql, state=state, county=county)
    data = rows_to_dict_list(cursor)
    return render_template("query4results.html", data=data)


def rows_to_dict_list(cursor):
    columns = [i[0] for i in cursor.description]
    return [dict(zip(columns, row)) for row in cursor]


if __name__ == '__main__':
    app.run()
