import psycopg2

#THIS IS DONE. NO NEED TO RUN AGAIN!

# connect to prostgres
conn = psycopg2.connect(
   database="postgres", user='postgres', password='password', host='127.0.0.1', port= '5432'
)
conn.autocommit = True

# initialize cursor
cursor = conn.cursor()

# create database
prompt = '''CREATE database protodata'''
cursor.execute(prompt)


# close the connection
conn.close()

