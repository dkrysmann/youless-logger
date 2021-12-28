import requests
import logging
import sqlite3 as sql
import pandas as pd
from datetime import datetime, timedelta

logger = logging.getLogger()

def convert_data(data):
    res = []
    time_format = '%Y-%m-%dT%H:%M:%S'
    timestamp = datetime.strptime(data['tm'], time_format) 
    for val in data['val']:
        if val:
            res.append({
                'time': timestamp,
                'energy_consumption' : int(val),
                'unit': data['un']
            })
        timestamp += timedelta(seconds=data['dt'])
        
    return res


def fetch_data():
    logger.info('Fetching new data')
    res = []
    reports = 3
    for i in range(reports):
        data = requests.get('http://youless/V?w={}&f=j'.format(i+1)).json()
        res += convert_data(data)
    return pd.DataFrame(res)


def store_data(df):
    # Read current data
    try:
        last_ts = pd.read_sql("SELECT MAX(time) AS time FROM youless", con)['time'][0]
    except Exception as e:
        logger.info('Error fetching last timestamp: {}'.format(e))
        last_ts = '1900-01-01'
    # Only keep data we don't have yet
    df = df[df['time'] > last_ts ]
    logger.info('Adding {} new row'.format(len(df)))
    df.to_sql('youless', con, if_exists='append')


if __name__ = 'main':
    con = sql.connect('youless.db')

    df = fetch_data()
    store_data(df)