from flask import Blueprint, render_template, request, jsonify
from .data_handler import *
from .graphs import *
import requests
import datetime

coisa = Blueprint('coisa', __name__)

# listen to post and get requests done to the home page of the website
@coisa.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        d = request.get_json()
        
        l = insert_row(d) # insert data in database

        # send post request to 'alerts' informing of new measurements in db
        requests.post("https://granlund.protopaja.aalto.fi/alerts", 
            json={},
            headers={"Content-Type": "application/json"},
        )

        l_table = create_light_plot()
        t_table = create_temp_plot()
        d_table = create_def_plot()

        draw = {'light' : l_table, 'temp' : t_table, 'def' : d_table}

        return render_template("home.html", date=l[0], time=l[1], light=l[2], temp=l[3], deflection=l[4], drawings=draw)

    else:
        d = get_last() # get most recent measurement

        l_table = create_light_plot()
        t_table = create_temp_plot()
        d_table = create_def_plot()

        draw = {'light' : l_table, 'temp' : t_table, 'def' : d_table}

        return render_template("home.html", date=d[1], time=d[2], light=d[3], temp=d[4], deflection=d[5], drawings=draw)


# listen to post and get requests done to the alert page of the website
@coisa.route('/alerts', methods=['GET', 'POST'])
def alerts():

    if request.method == 'POST':
        find_anomalies() # check & create anomalies from new measurements

    today = datetime.datetime.now()
    pretty = f'{today.day}/{today.month}/{today.year}'

    current_alerts = alert_today(pretty) # get anomalies registered today
    nots = get_not_today(pretty) # get anomalies from previous days

    return render_template("alerts.html", l=nots, todays=current_alerts, dt=pretty)


# listen to post and get requests done to the predictions page of the website
@coisa.route('/predictions')
def preds():
    dia = ["23 months", "23 months", "23 months"]

    return render_template("predictions.html", date=dia)


