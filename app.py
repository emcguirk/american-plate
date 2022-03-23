from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def welcome():  # put application's code here
    return render_template("welcome.html")


@app.route('/basic')
def basic():
    return render_template("basic_landing.html")


@app.route('/pro')
def pro():
    return render_template("pro_landing.html")


if __name__ == '__main__':
    app.run()
