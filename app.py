import sys
import cx_Oracle
import os
import json
from flask import Flask, render_template, request, redirect, url_for, session
from bokeh.embed import components
from bokeh.plotting import figure

app = Flask(__name__)

app.secret_key = '9263e93da73b4365a4d222d7c147fc29'

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
        SELECT y.year, y.state, sum(y.years_on_operation)/ 
        (SELECT COUNT(*) FROM years_on_operation y1 WHERE y.state = y1.state) avg_tenure
        FROM YEARS_ON_OPERATION y
        JOIN
        (SELECT * FROM (
        SELECT state, SUM(FARM_INCOME) FROM COMMODITY
        WHERE name = :commodity
        GROUP BY STATE
        ORDER BY SUM(FARM_INCOME) DESC)
        WHERE rownum < 6) t1
        ON y.state = t1.state
        GROUP BY y.year, y.state
    """
    cursor = connection.cursor()
    cursor.execute(sql, commodity=commodity)
    rows = cursor.fetchall()
    data = {
        'year': [2002, 2007, 2012, 2017]
    }

    length = 1
    for y in data['year']:
        for row in rows:
            if row[0] == y:
                if row[1] in data:
                    data[row[1]].append(row[2])
                else:
                    data[row[1]] = []
                    data[row[1]].append(row[2])
        for key in data:
            if len(data[key]) < length:
                data[key].append(0)

    p = figure(title="Change in Average Tenure in Farming", x_axis_label="year",
               y_axis_label="Average time on Operation")

    colors = ['blue', 'green', 'red', 'purple', 'cyan']
    i = 0
    for key in data:
        if key == 'year' or len(data[key]) == 0:
            continue
        p.line(data['year'], data[key], legend_label=key, line_width=2, color=colors[i])
        i += 1
    script, div = components(p)

    return render_template("query1results.html", bokehScript=script, bokehDiv=div)


@app.route('/pro/2', methods=['GET', 'POST'])
def query_two_form():
    if request.method == 'POST':
        animal = request.form.get('animal')
        vegetable = request.form.get('vegetable')
        return redirect(url_for('query_two_results', animal=animal, vegetable=vegetable))
    else:
        return render_template("query2landing.html")


@app.route('/pro/2/<animal>/<vegetable>')
def query_two_results(animal, vegetable):
    sql = """
        SELECT cr_year year, animal_income/veg_income ratio FROM
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
        order by year asc
        """
    cursor = connection.cursor()
    cursor.execute(sql, animal=animal, vegetable=vegetable)
    data = rows_to_dict_list(cursor)
    year = []
    ratio = []
    for item in data:
        year.append(item['YEAR'])
        ratio.append(item['RATIO'])
    p = figure(title="Ratio of meat to vegetable income", x_axis_label='Year', y_axis_label='Ratio')
    p.line(year, ratio, legend_label="Ratio", color='blue', line_width=2)
    script, div = components(p)

    return render_template("query2results.html", bokehScript=script, bokehDiv=div)


@app.route('/pro/3', methods=['GET', 'POST'])
def query_three_form():
    if request.method == 'POST':
        crop = request.form.get('Commodity')
        return redirect(url_for('query_three_results', crop=crop))
    sql = '''
    SELECT DISTINCT name FROM Crop
    '''
    cursor = connection.cursor()
    cursor.execute(sql)
    data = []
    for name in cursor.fetchall():
        data.append(name[0])
    return render_template("query3landing.html", data=data)


@app.route('/pro/3/<crop>')
def query_three_results(crop):
    sql = """
    SELECT c.region, cr.year, SUM(acres_harvested)
    FROM Commodity c
    JOIN
    CROP cr ON cr.State = c.State
    WHERE cr.name = :crop
    GROUP BY cr.year, c.region
    ORDER BY cr.year
    """
    cursor = connection.cursor()
    cursor.execute(sql, crop=crop)
    rows = cursor.fetchall()

    data = {
        'year': [2002, 2007, 2012, 2017],
        'Northeast': [],
        'West': [],
        'South': [],
        'Midwest': [],
    }

    length = 1
    for y in data['year']:
        for row in rows:
            if row[1] == y:
                data[row[0]].append(row[2])
        for key in data:
            if len(data[key]) < length:
                data[key].append(0)

    p = figure(title="Crop Production by Region", x_axis_label="year", y_axis_label="Acres Harvested")

    colors = ['blue', 'green', 'red', 'purple']
    i = 0
    for key in data:
        if key == 'year' or len(data[key]) == 0:
            continue
        p.line(data['year'], data[key], legend_label=key, line_width=2, color=colors[i])
        i += 1

    script, div = components(p)
    return render_template("query3results.html", data=data, bokehScript=script, bokehDiv=div)


@app.route('/pro/4', methods=['GET', 'POST'])
def query_four_form(state=""):
    state_query = '''
    SELECT DISTINCT state FROM LAND_VALUE ORDER BY STATE
    '''
    cursor = connection.cursor()
    cursor.execute(state_query)
    states = rows_to_dict_list(cursor)
    cursor.close()
    cursor = connection.cursor()

    county_query = '''
    SELECT DISTINCT COUNTY FROM LAND_VALUE 
    WHERE STATE LIKE :s
    ORDER BY COUNTY
    '''
    if request.method == 'POST' and request.form.get('county'):
        county = request.form.get('county')
        print(state)
        state = session['state']
        session.pop('state', None)
        return redirect(url_for('query_four_results', state=state, county=county))
    elif request.method == 'POST' and request.form.get('state'):
        s = request.form.get('state')
        print(s)
        print(type(s))
        session['state'] = s
        cursor.execute(county_query, s=s)
        counties = rows_to_dict_list(cursor)
        return render_template("query4landing.html", state=s, states=states, counties=counties)
    else:
        print(request.form.get('state'))
        return render_template("query4landing.html", states=states, counties={})


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
    ORDER BY year
    '''
    state = state.upper()
    county = county.upper()
    cursor = connection.cursor()
    cursor.execute(sql, state=state, county=county)
    data = rows_to_dict_list(cursor)

    year = []
    roi = []
    for row in data:
        year.append(row['YEAR'])
        roi.append(row['ROI'])
    p = figure(title="Yearly Return on Land Value in {0} County, {1}".format(county.title(), state),
               x_axis_label='Year',
               y_axis_label='Return on Value')
    p.line(year, roi, legend_label="Return on Asset Value", color='green', line_width=2)
    script, div = components(p)

    return render_template("query4results.html", bokehScript=script, bokehDiv=div)

@app.route('/pro/5', methods=['GET', 'POST'])
def query_five_form():
    if request.method == "POST":
        state = request.form.get('state')
        return redirect(url_for('query_five_results', state=state))
    else:
        sql = '''
        SELECT DISTINCT state FROM LAND_VALUE ORDER BY STATE
        '''
        cursor = connection.cursor()
        cursor.execute(sql)
        data = []
        for name in cursor.fetchall():
            data.append(name[0])
        return render_template("query5landing.html", states = data)
    

@app.route('/pro/5/<state>')
def query_five_results(state):
    sql = """
    SELECT f_year year, female_principals/total_acres ratio FROM
    (SELECT year f_year, state f_state, female_principals
    FROM FEMALE_PRINCIPALS f
    WHERE state = :state) female
    JOIN
    (SELECT year c_year, state c_state, sum(acres_harvested) total_acres
    FROM CROP c
    WHERE state = :state
    group by year, state) acres
    ON f_year = c_year
    ORDER BY year ASC
    """
    state = state.upper()
    cursor = connection.cursor()
    cursor.execute(sql, state=state)
    data = rows_to_dict_list(cursor)
    year = []
    ratio = []
    for item in data:
        year.append(item['YEAR'])
        ratio.append(item['RATIO'])
    print(year)
    print(ratio)
    p = figure(title="Ratio of Women Producers over Acres Harvested in {0}".format(state), x_axis_label='Year', y_axis_label='Producers / Acres')

    sql2 = """
    SELECT f_year year, female_principals/total_acres ratio FROM
    (SELECT year f_year, state f_state, female_principals
    FROM FEMALE_PRINCIPALS f
    WHERE state = :state) female
    JOIN
    (SELECT year c_year, state c_state, sum(herd_size) total_acres
    FROM LIVESTOCK c
    WHERE state = :state
    group by year, state) acres
    ON f_year = c_year
    ORDER BY year ASC
    """

    cursor.execute(sql2, state=state)
    data = rows_to_dict_list(cursor)
    year2 = []
    ratio2 = []
    for item in data:
        year2.append(item['YEAR'])
        ratio2.append(item['RATIO'])
    print(year2)
    print(ratio2)

    p.line(year, ratio, legend_label="Ratio: Women / Acres Harvested", color="blue", line_width=2)
    p.line(year2, ratio2, legend_label="Ratio: Women / Herd Size", color="orange", line_width=2)
    script, div = components(p)
    

    return render_template("query5results.html", bokehScript=script, bokehDiv=div)




def rows_to_dict_list(cursor):
    columns = [i[0] for i in cursor.description]
    return [dict(zip(columns, row)) for row in cursor]


if __name__ == '__main__':
    app.run()
