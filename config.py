import os

DEBUG = True
PATH_TO_FOLDER = f'{os.curdir}/blocks/'
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'decode_responses': True,
    'queue_db_num': 1,
    'removed_requests_db_num': 3,
    'demo_db_num': 2
}
