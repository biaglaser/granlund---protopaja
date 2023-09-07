import psycopg2
import random

def get_light():
    return random.randint(-10, 100)

def get_temp():
    return random.randint(-20, 310)

def get_def():
    return random.randint(-110, 110)

def new_hora(current):
    last_min = int(current[-2:])

    if last_min == 59: 
            last_min = 0
            if current[:2] != '23':
                int_time = int(current[:2]) + 1
                current = "{:02}".format(int_time)
            else:
                current = '00'
    else:
        last_min += 1

    
    if last_min < 10:
        f_time = "{}:0{}".format(current[:2], last_min)
    else:
        f_time = "{}:{}".format(current[:2], last_min)

    return f_time


#connect to db
conn = psycopg2.connect(
database="protodata", user='postgres', password='password', host='127.0.0.1', port= '5432'
)
conn.autocommit = True

# create cursor
cursor = conn.cursor()

# delete table if it already exists
cursor.execute("DROP TABLE IF EXISTS DUMMY CASCADE")

# create table
prompt ='''CREATE TABLE DUMMY(
   M_ID SERIAL PRIMARY KEY,
   DATE VARCHAR(15) NOT NULL,
   TIME VARCHAR(10) NOT NULL,
   LIGHT FLOAT,
   TEMP FLOAT,
   DEFLECTION FLOAT
)'''
cursor.execute(prompt)

# List of days for which you want to generate data
days = ["17/08/2023", "18/08/2023"]

hora = "00:00"

ok = False

# Loop over each day
for dia in days:
    while not ok:
        light = get_light()
        temp = get_temp()
        deflection = get_def()

        prompt = f'''INSERT INTO MEASUREMENTS(DATE, TIME, LIGHT, TEMP, DEFLECTION) VALUES ('{dia}', '{hora}', {light}, {temp}, {deflection})'''
        cursor.execute(prompt)

        hora = new_hora(hora)

        if hora == '00:00':
            ok = True

    ok = False


conn.commit()
# Close the connection
conn.close()