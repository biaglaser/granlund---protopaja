import psycopg2

# RUNNING THIS WILL EMPTY REGISTERED VALUES ON THE TABLE

# connect to prostgres db
conn = psycopg2.connect(
   database="protodata", user='postgres', password='password', host='127.0.0.1', port= '5432'
)
cursor = conn.cursor()

# delete table if it already exists
cursor.execute("DROP TABLE IF EXISTS ALERTS")

# create table
prompt ='''CREATE TABLE ALERTS(
   A_ID SERIAL PRIMARY KEY,
   MSG VARCHAR(1000) NOT NULL,
   TYPE VARCHAR(20) NOT NULL,
   MEASUREMENT INT NOT NULL REFERENCES MEASUREMENTS(M_ID)
)'''
cursor.execute(prompt)

# commit changes and close the connection
conn.commit()
conn.close()

