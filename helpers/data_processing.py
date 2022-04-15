import pandas as pd
import sqlite3 as sql
from config import DB_PATH


class YoulessData:
    data = None
    # Table names dictionary. Can be used for query formatting
    table_names = {}
    query = None

    def __init__(self):
        self.load_data()

    def load_data(self):
        with sql.connect(DB_PATH) as con:
            query = self.query.format(**self.table_names)
            try:
                data = pd.read_sql(query, con)
            except pd.io.sql.DatabaseError:
                data = None
            self.data = data


class EnergyDataMinute(YoulessData):
    table_names = {'minute_table': 'youless_minute'}
    query = '''
    WITH minute_data AS (
        SELECT 
            *,
            strftime('%H', time) AS hour,
            strftime('%M', time) AS minute,
            strftime('%Y-%m-%d', time) AS date,
			Cast((JulianDay(CURRENT_TIMESTAMP) - JulianDay(time)) * 24 As Integer) AS hour_diff
        FROM {minute_table}
    ), average AS (
        SELECT 
            AVG(energy_consumption) AS avg_energy_consumption,
            strftime('%H', time) AS hour,
            strftime('%M', time) AS minute
        FROM {minute_table}
        GROUP BY hour, minute
    )

    SELECT 
        * 
    FROM minute_data
    LEFT JOIN average USING(hour, minute)
    WHERE  hour_diff <= 12
    '''

class EnergyDataHour(YoulessData):
    table_names = {'hour_table': 'youless_hour'}
    query = '''
    WITH data AS (
        SELECT 
            *,
            strftime('%H', time) AS hour,
            strftime('%w', time) AS week_day,
            strftime('%Y-%m-%d', time) AS date
        FROM {hour_table}
    ), average AS (
        SELECT 
            AVG(energy_consumption) AS avg_energy_consumption,
            strftime('%H', time) AS hour
        FROM {hour_table}
        GROUP BY hour
    )

    SELECT 
        * 
    FROM data
    LEFT JOIN average USING(hour)
    ORDER BY time DESC
    LIMIT 24
    '''


class EnergyDataDay(YoulessData):
    table_names = {'day_table': 'youless_day', 'hour_table': 'youless_hour'}
    query = '''
    WITH data AS (
        SELECT 
            *,
            strftime('%w', time) AS week_day
        FROM {day_table}
    ), todays_energy AS (
        SELECT 
            strftime('%Y-%m-%d 00:00:00', time) AS time,
            SUM(energy_consumption)/1000 AS energy_consumption,
            'kWh' AS unit,
            strftime('%w', time) AS week_day
        FROM {hour_table}
        WHERE strftime('%Y-%m-%d', time) = CURRENT_DATE
        GROUP BY 1, week_day, unit
    ), average AS (
        SELECT 
            AVG(energy_consumption) AS avg_energy_consumption,
            strftime('%w', time) AS week_day
        FROM {day_table}
        GROUP BY week_day
    ), current_day_added AS (
        -- Current day needs to be filled with the hour data
        SELECT * FROM data
        UNION ALL
        SELECT * FROM todays_energy
    )

    SELECT 
        * 
    FROM current_day_added
    LEFT JOIN average USING(week_day)
    ORDER BY time DESC
    LIMIT 365
    '''

class EnergyDataMonth(YoulessData):
    table_names = {'day_table': 'youless_day'}
    query = '''
    SELECT 
        SUM(energy_consumption) AS energy_consumption,
        strftime('%Y-%m-01 00:00:00', time) AS time,
        strftime('%m', time) AS month,
        strftime('%Y', time) AS year
    FROM {day_table}
    GROUP BY year, month
    '''


class GasDataHour(EnergyDataHour):
    table_names = {'hour_table': 'youless_hour_gas'}


class GasDataDay(EnergyDataDay):
    table_names = {'day_table': 'youless_day_gas', 'hour_table': 'youless_hour_gas'}


class GasDataMonth(EnergyDataMonth):
    table_names = {'day_table': 'youless_day_gas'}
    


def load_data():    
    energy_minute = EnergyDataMinute()
    df_m = energy_minute.data

    energy_hour = EnergyDataHour()
    df_h = energy_hour.data

    energy_day = EnergyDataDay()
    df_day = energy_day.data

    energy_month = EnergyDataMonth()
    df_month = energy_month.data

    energy_hour = GasDataHour()
    df_h_gas = energy_hour.data

    gas_day = GasDataDay()
    df_day_gas = gas_day.data

    gas_month = GasDataMonth()
    df_month_gas = gas_month.data

    return {
        'minute': df_m, 
        'hour': df_h, 
        'hour_gas': df_h_gas,
        'day': df_day, 
        'day_gas': df_day_gas, 
        'month': df_month, 
        'month_gas': df_month_gas
    }

