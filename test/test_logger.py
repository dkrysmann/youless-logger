import datetime

from unittest import TestCase
from unittest.mock import patch, MagicMock

from logger import YoulessBaseLogger


class TestScraper(YoulessBaseLogger):
    youless_path = 'test_path'
    granularity = 'day'
    table_name = 'test_table'


class FetchDataTestCase(TestCase):
    @patch('logger.YoulessBaseLogger.store_data')
    @patch('logger.YoulessBaseLogger.convert_data')
    @patch('logger.requests.get')
    def test_fetching_for_day_granularity(
        self, mocked_get, mocked_convert_data, mocked_store_data
    ):
        """
        ... then the correct endpoint should have been called 12 times with correct parameters
        """
        data = {
            'un': 'Watt',
            'tm': '2022-04-10T00:00:00',
            'dt': 3600,
            'val': [
                ' 27',
                ' 33',
                ' 27',
                ' 33',
                ' 27',
                ' 33',
                ' 27',
                ' 26',
                ' 74',
                ' 53',
                ' 107',
                ' 86',
            ],
        }
        mocked_get.return_value = MagicMock(json=lambda: data)
        converted_data = YoulessBaseLogger.convert_data(data)
        mocked_convert_data.return_value = converted_data

        scraper = TestScraper()
        scraper.fetch_data()

        self.assertEqual(mocked_get.call_count, 12)
        mocked_store_data.assert_called_once()


class ConvertDataTestCase(TestCase):
    @patch('logger.requests.get')
    def test_data_provided(self, mocked_get):
        """
        ... then the data should be properly reformatted
        """
        data = {
            'un': 'Watt',
            'tm': '2022-04-10T00:00:00',
            'dt': 3600,
            'val': [' 27,1', ' 33'],
        }
        expected_timestamp = datetime.datetime(2022, 4, 10)
        expected_energy_consumption = [27.1, 33]
        excpected_unit = data['un']

        scraper = TestScraper()
        res = scraper.convert_data(data)
        first_row = res[0]
        energy_consumption = [e['energy_consumption'] for e in res]

        self.assertEqual(len(res), len(data['val']))
        self.assertEqual(first_row['time'], expected_timestamp)
        self.assertEqual(first_row['unit'], excpected_unit)
        self.assertCountEqual(energy_consumption, expected_energy_consumption)
