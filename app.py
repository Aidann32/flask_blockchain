import redis
from flask import Flask, render_template
from loguru import logger
import logging
import atexit

import config
from repository.redis.repository import RedisRepository
from repository.file_storage.repository import FileRepository
from service.blockchain import BlockchainService
from service.queue import QueueService


app = Flask(__name__, template_folder='web_service/templates')

app.logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('logger/flask_logs.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)

try:
    # add storage of removed requests transactions
    storage = redis.Redis(host=config.REDIS_CONFIG['host'], db=config.REDIS_CONFIG['queue_db_num'], port=config.REDIS_CONFIG['port'], decode_responses=config.REDIS_CONFIG['decode_responses'])
    demo_storage = redis.Redis(host=config.REDIS_CONFIG['host'], db=config.REDIS_CONFIG['demo_db_num'], port=config.REDIS_CONFIG['port'], decode_responses=config.REDIS_CONFIG['decode_responses'])
    r = RedisRepository(storage)
    demo_repository = RedisRepository(demo_storage)
except Exception as e:
    r = FileRepository(path_to_folder=config.PATH_TO_FOLDER)
    print(e)

logger.add("logger/service_logs.log", format="{time} {level} {message}", level="INFO")
service = BlockchainService(repository=r, logger=logger)
demo_service = BlockchainService(repository=demo_repository, logger=logger)
queue_service = QueueService(service)

if config.DEBUG:
    from populate_blockchain import populate_blockchain
    populate_blockchain(queue_service)


def cleanup():
    r.delete_all_keys()


atexit.register(cleanup)


@app.route("/", methods=['GET'])
def main():
    return render_template('index.html')


# TODO: Remove block by blockchain logic
# Add transaction when removing request from network. Search completed transactions in other DB
# TODO: Add validation when adding request(If request with IIN exists, if request is on right place)
