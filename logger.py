import requests
import logging
import sqlite3 as sql
import pandas as pd
from datetime import datetime, timedelta
from config import DB_PATH, GAS_ENABLED


logging.basicConfig(
    format='%(name)s: %(asctime)s %(levelname)s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
)


class YoulessBaseLogger:
    GRANULARITY_MAP = {
        'minute': {'param': 'h', 'reports': 20},
        'hour': {'param': 'd', 'reports': 70},
        'day': {'param': 'm', 'reports': 12},
    }
    con = None
    cur = None
    report_param = None
    report_pages = None
    table_name = None
    chart_data = pd.DataFrame()
    endpoint = 'http://192.168.1.14/'
    default_params = {'f': 'j'}  # JSON response format,

    def __init__(self):
        self.report_param = self.GRANULARITY_MAP[self.granularity]['param']
        self.report_pages = self.GRANULARITY_MAP[self.granularity]['reports']
        self.logger = logging.getLogger(
            'Youless Scraper {}'.format(self.__class__.__name__)
        )

    @property
    def youless_path(self) -> str:
        raise NotImplementedError(
            'youless_path attribute needs to be implemented in deriving class'
        )

    @property
    def table_name(self) -> str:
        raise NotImplementedError(
            'table_name attribute needs to be implemented in deriving class'
        )

    @property
    def granularity(self) -> str:
        raise NotImplementedError(
            'granularity attribute needs to be implemented in deriving class'
        )

    @property
    def endpoint(self) -> str:
        return f'http://192.168.1.14/{self.youless_path}'

    def fetch_data(self):
        self.logger.info('Fetching new data for {} reports'.format(self.report_pages))
        res = []
        for page in range(self.report_pages):
            data = requests.get(
                self.endpoint,
                params={**self.default_params, self.report_param: page + 1},
            )
            res += YoulessBaseLogger.convert_data(data.json())
        self.logger.info('Received {} entries'.format(len(res)))
        self.store_data(pd.DataFrame(res))

    @staticmethod
    def convert_data(data: dict) -> list:
        res = []
        time_format = '%Y-%m-%dT%H:%M:%S'
        timestamp = datetime.strptime(data['tm'], time_format)
        for val in data['val']:
            if val and val != '*':
                res.append(
                    {
                        'time': timestamp,
                        'energy_consumption': float(val.replace(',', '.')),
                        'unit': data['un'],
                    }
                )
            timestamp += timedelta(seconds=data['dt'])

        return res

    def table_exists(self) -> bool:
        query = '''
        SELECT name 
        FROM sqlite_master 
        WHERE 
            type='table'
            AND name='{table_name}'; 
        '''

        with sql.connect(DB_PATH) as con:
            cur = con.cursor()
            listOfTables = cur.execute(
                query.format(table_name=self.table_name)
            ).fetchall()
        return len(listOfTables) > 0

    def store_data(self, df):
        if df.empty:
            self.logger.info('No data to be stored')
            return
        with sql.connect(DB_PATH) as con:
            if not self.table_exists():
                self.logger.warning(
                    f'Table {self.table_name} does not exist. Creating...'
                )
                # Just upload all data and create the table
                df.to_sql(self.table_name, con, index=False)
                value_count = len(df)
            else:
                # Store to temporary db
                df.to_sql('tmp', con, if_exists='replace', index=False)

                # Update existing data
                query = '''
                UPDATE {table_name} AS old
                SET energy_consumption = (
                    SELECT energy_consumption
                    FROM tmp
                    WHERE time = old.time
                    LIMIT 1
                ) 
                WHERE EXISTS (
                    SELECT energy_consumption
                    FROM tmp
                    WHERE time = old.time
                )
                '''

                cur = con.cursor()
                cur.execute(query.format(table_name=self.table_name))
                con.commit()
                self.logger.info('Updated {} old values'.format(cur.rowcount))

                # Store new data
                query = '''
                INSERT INTO {table_name} (time, energy_consumption, unit)
                SELECT time, energy_consumption, unit
                FROM tmp AS new
                WHERE NOT EXISTS (
                    SELECT 1 FROM {table_name} old 
                    WHERE old.time = new.time
                );
                '''

                cur = con.cursor()
                cur.execute(query.format(table_name=self.table_name))
                con.commit()
                value_count = cur.rowcount

            self.logger.info('Uploaded {} new values'.format(value_count))


class YoulessEnergyMinute(YoulessBaseLogger):
    youless_path = 'V'
    table_name = 'youless_minute'
    granularity = 'minute'


class YoulessEnergyHour(YoulessBaseLogger):
    youless_path = 'V'
    table_name = 'youless_hour'
    granularity = 'hour'


class YoulessEnergyDay(YoulessBaseLogger):
    youless_path = 'V'
    table_name = 'youless_day'
    granularity = 'day'


class YoulessGasHour(YoulessBaseLogger):
    youless_path = 'W'
    table_name = 'youless_hour_gas'
    granularity = 'hour'


class YoulessGasDay(YoulessBaseLogger):
    youless_path = 'W'
    table_name = 'youless_day_gas'
    granularity = 'day'


if __name__ == '__main__':
    energy_minute_scraper = YoulessEnergyMinute()
    energy_minute_scraper.fetch_data()
    energy_hour_scraper = YoulessEnergyHour()
    energy_hour_scraper.fetch_data()
    energy_day_scraper = YoulessEnergyDay()
    energy_day_scraper.fetch_data()

    if GAS_ENABLED:
        gas_hour_scraper = YoulessGasHour()
        gas_hour_scraper.fetch_data()
        gas_day_scraper = YoulessGasDay()
        gas_day_scraper.fetch_data()
