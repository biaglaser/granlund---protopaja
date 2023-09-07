import psycopg2
import datetime
import requests

#here are readable forms of the addresses showing sensors. edit it with the proper addresses
SENSORS = {'light': ['addr1'], 'temp': ['addr2'], 'deflection': ['addr3']}


"""Insert the received data into the MEASUREMENTS table in the postgres
database PROTODATA.

Keyword arguments:
- values -- json object describing measurements, following a specific template.
Return: 
- list describing info of the last registered measurement, following the format
and order: [date, time, address, value].
"""
def insert_row(values):

    #connect to db
    conn = psycopg2.connect(
    database="protodata", user='postgres', password='password', host='127.0.0.1', port= '5432'
    )
    conn.autocommit = True

    # create cursor
    cursor = conn.cursor()

    #gateway = values["gateway_ID"]
    today = datetime.datetime.now()
    pretty = f'{today.day}/{today.month}/{today.year}'

    #creating and executing sql prompts for database
    for key in values:
        for meas in values[key]:
            t = meas[0]
            addr = "'" + str(key) + "'"
            v = meas[1]

            prompt = f'''INSERT INTO MEASUREMENTS(DATE, TIMESTAMP, ADDR, VALUE) VALUES ('{pretty}', '{t}', {addr}, {v})'''
            cursor.execute(prompt)

            find_anomalies()


    #determine last measurement made
    last = [today, t, addr, v]
    
    # commit database changes and close connection
    conn.commit()
    conn.close()

    return last


"""
Find the last measurement registered.

Return:
- list describing info of the last registered measurement, following the format
and order: [date, time, address, value].
"""
def get_last():
    #connect to db
    conn = psycopg2.connect(
    database="protodata", user='postgres', password='password', host='127.0.0.1', port= '5432'
    )
    conn.autocommit = True

    # create cursor
    cursor = conn.cursor()

    # get last measurement
    cursor.execute('SELECT * FROM MEASUREMENTS ORDER BY M_ID DESC LIMIT 1;')
    
    row = cursor.fetchall()

    # close connection
    conn.close()

    # check if there are any measurements
    try:
        row_tuple = row[0]
        row_l = list(row_tuple)
    except IndexError:
        row_l = ['no measurement'] * 5

    return row_l


"""
Check newest measurements for anomalies.
"""
def find_anomalies():
    #connect to db
    conn = psycopg2.connect(
    database="protodata", user='postgres', password='password', host='127.0.0.1', port= '5432'
    )
    conn.autocommit = True

    # initialize cursor
    cursor = conn.cursor()

    # select five last measurements
    cursor.execute('SELECT * FROM MEASUREMENTS ORDER BY M_ID DESC LIMIT 1;')
    
    row_bad = cursor.fetchall()
    #(id, date, time, add, v)

    row = []
    for i in row_bad[0]:
        row.append(i)


    if row[3] in SENSORS['light']:
        #check light
        if int(row[4]) < 1:
            sql = f"ALERT! The measurement made on {row[1]} at {row[2]} indicates a data anomaly for light brightness value: luminosity level ({row[4]}) is lower than optimal."
            create_alert(row[0], sql, 'light')

    elif row[3] in SENSORS['temp']:
        #check temp
        if int(row[4]) < -10 or int(row[4]) > 300:
            sql = f"ALERT! The measurement made on {row[1]} at {row[2]} indicates a data anomaly for temperature value: material temperature ({row[4]}) has reached an extreme level."
            create_alert(row[0], sql, 'temp')

    elif row[3] in SENSORS['deflection']:
        #check def
        if int(row[4]) > 100 or int(row[4]) < -100:
            sql = f"ALERT! The measurement made on {row[1]} at {row[2]} indicates a data anomaly for deflection value: high acceleration ({row[4]}) was detected on the tip of the tower."
            create_alert(row[0], sql, 'def')



"""
Function to create alerts from data anomalies.

Keyword arguments:
- id_num -- int M_ID value for the measurement with an anomaly
- msg -- string alert message explaining anomaly
- tipo -- sring saying which sensor raised the anomaly
"""
def create_alert(id_num, msg, tipo):
    #connect to db
    conn = psycopg2.connect(
    database="protodata", user='postgres', password='password', host='127.0.0.1', port= '5432'
    )
    conn.autocommit = True

    # create cursor
    cursor = conn.cursor()

    # create row in ALERTS table registering the alert message and type of sensor
    prompt = f'''INSERT INTO ALERTS(MSG, TYPE, MEASUREMENT) VALUES ('{msg}', '{tipo}', '{id_num}')'''
    cursor.execute(prompt)

    # commit changes and close connection
    conn.commit()
    conn.close()


"""
Find the data anomalies registered on previous days

Keyword arguments:
- dia -- string describing current date, in format "dd/mm/yyyy"
Return: 
- dictionary showing alerts made in previous days.
    . keys = type of sensor
    . values = list of alerts by given key sensor
"""
def get_not_today(dia):
    #connect to db
    conn = psycopg2.connect(
    database="protodata", user='postgres', password='password', host='127.0.0.1', port= '5432'
    )
    conn.autocommit = True

    # initialize cursor
    cursor = conn.cursor()
   
    # select from alerts table the registered anomalies from previous days
    sql = "SELECT TYPE, MSG FROM ALERTS A, MEASUREMENTS M WHERE (A.MEASUREMENT = M.M_ID) AND to_date(M.DATE,'DD/MM/YYYY')!=to_date('" + dia +"','DD/MM/YYYY') ORDER BY A.A_ID DESC LIMIT 10;"
    cursor.execute(sql)

    rows = cursor.fetchall()

    # close connection
    conn.close()

    # create dictionary with sensor keys and anomalies as values
    rows_dic = {}
    for row in rows:
        if row[0] not in rows_dic.keys():
            rows_dic[row[0]] = []
        rows_dic[row[0]].append(row[1])

    print(rows_dic)
            

    return rows_dic


"""
Find the data anomalies registered on current day

Keyword arguments:
- dia -- string describing current date, in format "dd/mm/yyyy"
Return: 
- dictionary showing alerts made in current day.
    . keys = type of sensor
    . values = list of alerts by given key sensor
"""
def alert_today(dia):
    #connect to db
    conn = psycopg2.connect(
    database="protodata", user='postgres', password='password', host='127.0.0.1', port= '5432'
    )
    conn.autocommit = True

    # initialize cursor
    cursor = conn.cursor()

    # select from alerts table the registered anomalies from current day
    sql = "SELECT TYPE, MSG FROM ALERTS A, MEASUREMENTS M WHERE (A.MEASUREMENT = M.M_ID) AND to_date(M.DATE,'DD/MM/YYYY')=to_date('" + dia +"','DD/MM/YYYY') ORDER BY A.A_ID DESC;"
    cursor.execute(sql)

    rows = cursor.fetchall()

    # close connection
    conn.close()

    # create dictionary with sensor keys and anomalies as values
    rows_dic = {}
    for row in rows:
        if row[0] not in rows_dic.keys():
            rows_dic[row[0]] = []
        rows_dic[row[0]].append(row[1])

    print(rows_dic)

    return rows_dic
