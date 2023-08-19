import psycopg2

"""Handle datetime string by creating a timestamp for each measurement
and formatting the times and date.

Keyword arguments:
- date_string -- string describing date and time of first measurement, in format "ddmmyyyyhhmm"
Return: 
- string for date, in format "dd/mm/yyyy"
- list for measurement times (5), each item in format "hh:mm"
"""
def get_times(date_string):

    # format date string
    final_date = date_string[:2] + "/" + date_string[2:4] + "/" + date_string[4:8]
    
    # create formatted timestamps for each measurement
    times = []

    first_time = date_string[8:10] + ":" + date_string[10:]
    times.append(first_time.strip())


    last_min = int(first_time[-2:]) + 1
    
    if last_min < 10:
        f_time = "{}:0{}".format(first_time[:2], last_min)
    else:
        f_time = "{}:{}".format(first_time[:2], last_min)

    times.append(f_time.strip())

    for i in range(1, 4):
        if last_min == 59: 
            last_min = 0
            if first_time[:2] != '23':
                int_time = int(first_time[:2]) + 1
                first_time = str(int_time)
            else:
                first_time = '00'

        else:
            last_min += 1

        if last_min < 10:
            i_time = "{}:0{}".format(first_time[:2], last_min)
        else:
            i_time = "{}:{}".format(first_time[:2], last_min)
        times.append(i_time.strip())

    return final_date.strip(), times


"""Insert the received data into the MEASUREMENTS table in the postgres
database PROTODATA.

Keyword arguments:
- values -- json object describing measurements, following a specific template.
Return: 
- list describing info of the last registered measurement, following the format
and order: [date, time, light, temp, deflection].
"""
def insert_row(values):

    #connect to db
    conn = psycopg2.connect(
    database="protodata", user='postgres', password='password', host='127.0.0.1', port= '5432'
    )
    conn.autocommit = True

    # create cursor
    cursor = conn.cursor()

    #fix date string and get time values
    info = values["datetime"]
    date, times = get_times(info)

    #gateway = values["gateway_ID"]

    #creating and executing sql prompts for database
    for i in range(0, 5):
        t = times[i]
        light = values["light"][i]
        temp = values["temperature"][i]
        deflection = values["deflection"][i]

        prompt = f'''INSERT INTO MEASUREMENTS(DATE, TIME, LIGHT, TEMP, DEFLECTION) VALUES ('{date}', '{t}', {light}, {temp}, {deflection})'''
        cursor.execute(prompt)


    #determine last measurement made
    last = [date, t, str(light), str(temp), str(deflection)]
    
    # commit database changes and close connection
    conn.commit()
    conn.close()

    return last


"""
Find the last measurement registered.

Return:
- list describing info of the last registered measurement, following the format
and order: [date, time, light, temp, deflection].
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
        row_l = ['no measurement'] * 6

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
    cursor.execute('SELECT * FROM MEASUREMENTS ORDER BY M_ID DESC;')
    
    rows = cursor.fetchall()
    
    # make copy of the seleected rows and invert it
    rows_copy = rows
    rows_copy.reverse()

    # close connection to db
    conn.close()

    # initialize dictionary with sensors as keys
    alert_dic = {'light' : [], 'temp' : [], 'def' : []}

    count = 0

    #check data for anomalies, create alert messages when necessary
    for row in rows:
        #check light
        if int(row[3]) < 1:
            info = rows_copy[count]
            alert_dic['light'].append(f"ALERT! The measurement made on {info[1]} at {info[2]} indicates a data anomaly for light brightness value: luminosity level ({info[3]}) is lower than optimal.")
        else:
            alert_dic['light'].append('normal')
        
        #check temp
        if int(row[4]) < -10 or int(row[4]) > 300:
            info = rows_copy[count]
            alert_dic['temp'].append(f"ALERT! The measurement made on {info[1]} at {info[2]} indicates a data anomaly for temperature value: material temperature ({info[4]}) has reached an extreme level.")
        else:
            alert_dic['temp'].append('normal')

        #check def
        if int(row[5]) > 100 or int(row[5]) < -100:
            info = rows_copy[count]
            alert_dic['def'].append(f"ALERT! The measurement made on {info[1]} at {info[2]} indicates a data anomaly for deflection value: high acceleration ({info[5]}) was detected on the tip of the tower.")
        else:
            alert_dic['def'].append('normal')

        count += 1
    

    #create alerts where necessary
    for key in alert_dic: #iterate through sensors
        i = 0
        while i < 5: #iterate through measurements
            if alert_dic[key][i] != 'normal':
                info = rows_copy[i]
                n = int(info[0])

                create_alert(n, alert_dic[key][i], key)
            
            i += 1



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

    return rows_dic
