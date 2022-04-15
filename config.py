import os
import json

repository_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(repository_path, 'config.json')
with open(config_path, 'r') as j:
    CONFIG = json.loads(j.read())

DB_PATH = CONFIG['db_path']
DEBUG_MODE = CONFIG['debug_mode']
GAS_ENABLED = CONFIG.get('gas_enabled')
