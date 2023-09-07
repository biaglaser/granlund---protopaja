from flask import Blueprint, render_template, request, jsonify
from .data_handler import *
from .graphs import *
from .formatting import *
import requests
import datetime

coisa = Blueprint('coisa', __name__)

# listen to post and get requests done to the home page of the website
@coisa.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        #d = request.get_json()
        data = request.get_data(as_text=True)
        d = create_json(data)

        l = insert_row(d) # insert data in database

        # send get request to 'alerts' to update page
        requests.get("https://granlund.protopaja.aalto.fi/alerts", 
        json={},
        headers={"Content-Type": "application/json"},
        )

        draw = create_graphs()
        print(draw)

        return render_template("home.html", date=l[0], time=l[1], add=l[2], val=l[3], drawings=draw)

    else:
        d = get_last() # get most recent measurement

        draw = create_graphs()
        print(draw)

        return render_template("home.html", date=d[1], time=d[2], add=d[3], val=d[4], drawings=draw)


# listen to post and get requests done to the alert page of the website
@coisa.route('/alerts', methods=['GET', 'POST'])
def alerts():
    today = datetime.datetime.now()
    pretty = f'{today.day}/{today.month}/{today.year}'

    current_alerts = alert_today(pretty) # get anomalies registered today
    nots = get_not_today(pretty) # get anomalies from previous days

    return render_template("alerts.html", l=nots, todays=current_alerts, dt=pretty)


# listen to post and get requests done to the predictions page of the website
@coisa.route('/predictions')
def preds():
    #place holder times.
    dia = ["23 months", "23 months", "23 months"]

    return render_template("predictions.html", date=dia)

