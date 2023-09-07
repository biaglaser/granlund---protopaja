import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

'''Function to create graphs based on the values on the database. These graphs are displayed on the homepage of the website.
They are saved on the website/static/ folder.'''
def create_graphs():
    #connect to db
    conn = psycopg2.connect(
    database="protodata", user='postgres', password='password', host='127.0.0.1', port= '5432'
    )
    conn.autocommit = True

    # create cursor
    cursor = conn.cursor()

    sql = "SELECT DISTINCT ADDR FROM MEASUREMENTS"
    df = pd.read_sql_query(sql, conn)

    addr_list = df['addr'].tolist()

    #sql query to retreive data
    sql2 = "SELECT * FROM MEASUREMENTS ORDER BY DATE, TIMESTAMP"

    # Read data into a pandas DataFrame
    df2 = pd.read_sql_query(sql2, conn)

    tables = {}

    for sensor in addr_list:
        specific_df = df2[df2['addr'] == sensor]

        # Plot data
        plt.figure(figsize=(10, 5))
        plt.plot(specific_df['date'], specific_df['value'], marker='o')
        plt.title(f'Measured values from {sensor}')
        plt.xlabel('Date')
        plt.ylabel('Values')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f'website/static/{sensor}_plot.png')

        desc_df = specific_df['value'].describe()
        filtered_desc_df = desc_df.loc[['count', 'mean', 'max', 'min']]

        filtered_desc_df = filtered_desc_df.round(2)

        filtered_desc_df = pd.DataFrame(filtered_desc_df).reset_index()
        filtered_desc_df.columns = ['Statistic', 'Value']  # Giving meaningful column names
        table_def = filtered_desc_df.to_html(classes='table table-bordered').replace('<table border="1" class="dataframe">','<table class="table table-striped">')

        tables[sensor] = table_def

    # Close the connection
    conn.close()

    return tables