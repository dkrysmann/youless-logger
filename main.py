import requests
import logging
import sqlite3 as sql
import pandas as pd
from datetime import datetime, timedelta

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('youless')


GRANULARITY_MAP = {
    'minute': {'param': 'h', 'reports': 20, 'db': 'youless_minute'},
    'hour': {'param': 'd', 'reports': 70, 'db': 'youless_hour'}
}

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


def fetch_data(granularity='minute'):
    param = GRANULARITY_MAP[granularity]['param']
    reports = GRANULARITY_MAP[granularity]['reports']

    logger.info('Fetching new data. Granularity: {}, reports: {}'.format(granularity, reports))
    res = []
    for i in range(reports):
        data = requests.get('http://youless/V?{param}={page}&f=j'.format(
            param=param,
            page=i+1
        )).json()
        res += convert_data(data)
    logger.info('Received {} entries'.format(len(res)))
    return pd.DataFrame(res)


def store_data(df, con):
    # Read current data
    db = GRANULARITY_MAP[granularity]['db']
    try:
        last_ts = pd.read_sql("SELECT MAX(time) AS time FROM {}".format(db), con)['time'][0]
    except Exception as e:
        logger.info('Error fetching last timestamp - uploading all. Error: {}'.format(e))
        last_ts = '1900-01-01'
    # Only keep data we don't have yet
    df = df[df['time'] > last_ts ]
    logger.info('Adding {} new rows'.format(len(df)))
    df.to_sql(db, con, if_exists='append', index=False)


if __name__ == '__main__':
    granularity = 'minute'
    with sql.connect('youless.db') as con:
        granularity = 'minute'
        df = fetch_data(granularity)
        store_data(df, con)

        granularity = 'hour'
        df = fetch_data(granularity)
        store_data(df, con)
