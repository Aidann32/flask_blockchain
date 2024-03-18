import hashlib
import redis
from flask import render_template, redirect, url_for, request, abort, Flask
from loguru import logger
import logging
import atexit
from datetime import date

import config
from repository.redis.repository import RedisRepository
from repository.file_storage.repository import FileRepository
from service.blockchain import BlockchainService
from service.queue import QueueService
from utils.utils import create_folder_and_file, extract_text_from_docx
from models.queue import *

create_folder_and_file("logger", "flask_logs.log")
create_folder_and_file("logger", "service_logs.log")

app = Flask(__name__, template_folder='web_service/templates')

app.logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('logger/flask_logs.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)

try:
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


@app.route("/queue", methods=["GET"])
def queue_main():
    return render_template("queue/index.html")


@app.route("/queue/request", methods=["GET", "POST"])
def queue_request():
    if request.method == "POST":
        if 'document' not in request.files:
            return "File is not uploaded", 400
        file = request.files['document']
        text = ""
        if file.filename == '':
            return "No selected file", 400
        if file:
            text = extract_text_from_docx(file)

        if not text:
            return "File is empty", 400

        document_hash = hashlib.sha256(text.encode()).hexdigest()
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        iin = request.form["iin"]
        phone_number = request.form["phone_number"]
        longitude = float(request.form["longitude"])
        latitude = float(request.form["latitude"])
        area = float(request.form["area"])
        state = request.form["state"]
        soil_type = request.form["soil_type"]

        location = Location(longitude=longitude, latitude=latitude)
        applicant = Applicant(first_name=first_name, last_name=last_name, iin=iin, phone_number=phone_number)
        land_plot = LandPlot(area=area, location=location, state=state, soil_type=soil_type)
        place = queue_service.place + 1
        queue_request = QueueRequest(document_hash=document_hash, land=land_plot, applicant=applicant, place=place, removed_at=None)
        queue_service.enqueue(queue_request.to_dict())
        queue_service.place += 1
        return redirect(url_for("queue_index"))
    return render_template("queue/request_form.html")


@app.route("/queue/search", methods=["GET", "POST"])
def search_request():
    if request.method == "POST":
        document_hash = request.form["document_hash"]
        request_block = queue_service.find_key_by_document_hash(document_hash)
        print(request_block)
        return render_template("queue/search_request.html", request_block=request_block)
    return render_template("queue/search_request.html")


@app.route("/dequeue", methods=["POST"])
def dequeue():
    pass

@app.route("/queue_view", methods=["GET", "POST"])
def queue_view():
    pass


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text = request.form["text"]
        if len(text) < 1:
            return redirect(url_for("index"))

        make_proof = request.form.get("make_proof", False)
        demo_service.write_block(text, make_proof)
        return redirect(url_for("index"))
    return render_template("index.html")


@app.route("/check", methods=["POST"])
def integrity():
    results = demo_service.check_blocks_integrity()
    if request.method == "POST":
        return render_template("index.html", results=results)
    return render_template("index.html")


@app.route("/mining", methods=["POST"])
def mining():
    if request.method == "POST":
        max_index = int(demo_service.get_next_index())
        for i in range(2, max_index):
            demo_service.get_pow(i)
        return render_template("index.html", querry=max_index)
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)


# TODO: Search block by document hash
# TODO: Display in HTML
# TODO: Remove block by blockchain logic
# TODO: Add statuses to request
# TODO: Add validation when adding request(If request with IIN exists, if request is on right place)
