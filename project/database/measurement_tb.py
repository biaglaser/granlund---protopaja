import psycopg2

# RUNNING THIS WILL EMPTY REGISTERED VALUES ON THE TABLE

# connect to prostgres db
conn = psycopg2.connect(
   database="protodata", user='postgres', password='password', host='127.0.0.1', port= '5432'
)
cursor = conn.cursor()

# delete table if it already exists
cursor.execute("DROP TABLE IF EXISTS MEASUREMENTS CASCADE")

# create table
prompt ='''CREATE TABLE MEASUREMENTS(
   M_ID SERIAL PRIMARY KEY,
   DATE VARCHAR(15) NOT NULL,
   TIME VARCHAR(10) NOT NULL,
   LIGHT FLOAT,
   TEMP FLOAT,
   DEFLECTION FLOAT
)'''
cursor.execute(prompt)

# commit changes and close the connection
conn.commit()
conn.close()
