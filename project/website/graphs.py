import psycopg2
import pandas as pd
import matplotlib.pyplot as plt


def create_light_plot():
    #connect to db
    conn = psycopg2.connect(
    database="protodata", user='postgres', password='password', host='127.0.0.1', port= '5432'
    )
    conn.autocommit = True

    # create cursor
    cursor = conn.cursor()

    #sql query to retreive data
    sql = "SELECT DATE, TIME, LIGHT FROM MEASUREMENTS ORDER BY DATE"

    # Read data into a pandas DataFrame
    df = pd.read_sql_query(sql, conn)

    # Close the connection
    conn.close()

    # Combine date and time columns into a single datetime column
    df['datetime'] = pd.to_datetime(df['date'].astype(str) + ' ' + df['time'].astype(str))

    # Plot data
    plt.figure(figsize=(10, 5))
    plt.plot(df['datetime'], df['light'], marker='o')
    plt.title('Measured light intensity values - line graph')
    plt.xlabel('Date')
    plt.ylabel('Light')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('website/static/light_plot.png')

    desc_df = df['light'].describe()
    filtered_desc_df = desc_df.loc[['count', 'mean', 'max', 'min']]

    filtered_desc_df = pd.DataFrame(filtered_desc_df).reset_index()
    filtered_desc_df.columns = ['Statistic', 'Value']  # Giving meaningful column names
    table_light = filtered_desc_df.to_html(classes='table table-bordered').replace('<table border="1" class="dataframe">','<table class="table table-striped">')


    return table_light


def create_temp_plot():
    #connect to db
    conn = psycopg2.connect(
    database="protodata", user='postgres', password='password', host='127.0.0.1', port= '5432'
    )
    conn.autocommit = True

    # create cursor
    cursor = conn.cursor()

    #sql query to retreive data
    sql = "SELECT DATE, TIME, TEMP FROM MEASUREMENTS ORDER BY DATE"

    # Read data into a pandas DataFrame
    df = pd.read_sql_query(sql, conn)

    # Close the connection
    conn.close()

    # Combine date and time columns into a single datetime column
    df['datetime'] = pd.to_datetime(df['date'].astype(str) + ' ' + df['time'].astype(str))

    print(df)

    # Plot data
    plt.figure(figsize=(10, 5))
    plt.plot(df['datetime'], df['temp'], marker='o')
    plt.title('Measured material temperature values - line graph')
    plt.xlabel('Date')
    plt.ylabel('Temperature')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('website/static/temp_plot.png')

    desc_df = df['temp'].describe()
    filtered_desc_df = desc_df.loc[['count', 'mean', 'max', 'min']]
 
    filtered_desc_df = pd.DataFrame(filtered_desc_df).reset_index()
    filtered_desc_df.columns = ['Statistic', 'Value']  # Giving meaningful column names
    table_temp = filtered_desc_df.to_html(classes='table table-bordered').replace('<table border="1" class="dataframe">','<table class="table table-striped">')

    
    return table_temp


def create_def_plot():
    #connect to db
    conn = psycopg2.connect(
    database="protodata", user='postgres', password='password', host='127.0.0.1', port= '5432'
    )
    conn.autocommit = True

    # create cursor
    cursor = conn.cursor()

    #sql query to retreive data
    sql = "SELECT DATE, TIME, DEFLECTION FROM MEASUREMENTS ORDER BY DATE"

    # Read data into a pandas DataFrame
    df = pd.read_sql_query(sql, conn)

    # Close the connection
    conn.close()

    # Combine date and time columns into a single datetime column
    df['datetime'] = pd.to_datetime(df['date'].astype(str) + ' ' + df['time'].astype(str))

    print(df)

    # Plot data
    plt.figure(figsize=(10, 5))
    plt.plot(df['datetime'], df['deflection'], marker='o')
    plt.title('Measured deflection values - line graph')
    plt.xlabel('Date')
    plt.ylabel('Deflection')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('website/static/def_plot.png')

    desc_df = df['deflection'].describe()
    filtered_desc_df = desc_df.loc[['count', 'mean', 'max', 'min']]

    filtered_desc_df = pd.DataFrame(filtered_desc_df).reset_index()
    filtered_desc_df.columns = ['Statistic', 'Value']  # Giving meaningful column names
    table_def = filtered_desc_df.to_html(classes='table table-bordered').replace('<table border="1" class="dataframe">','<table class="table table-striped">')

    
    return table_def

