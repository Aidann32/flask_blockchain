import hashlib
import redis
from flask import render_template, redirect, url_for, request, abort, Flask
from loguru import logger
import logging

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
    storage = redis.Redis(host=config.REDIS_CONFIG['host'], port=config.REDIS_CONFIG['port'], decode_responses=config.REDIS_CONFIG['decode_responses'])
    r = RedisRepository(storage)
except Exception as e:
    r = FileRepository(path_to_folder=config.PATH_TO_FOLDER)
    print(e)

logger.add("logger/service_logs.log", format="{time} {level} {message}", level="INFO")
service = BlockchainService(repository=r, logger=logger)
queue_service = QueueService(service)


# def cleanup():
#     r.delete_all_keys()
#
#
# @app.teardown_appcontext
# def teardown_appcontext(error=None):
#     cleanup()

@app.route("/queue", methods=["GET", "POST"])
def queue_index():
    if request.method == "POST":
        if 'file' not in request.files:
            return "File is not uploaded", 400
        file = request.files['file']
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
        longtitude = float(request.form["longtitude"])
        latitude = float(request.form["latitude"])
        area = float(request.form["area"])
        state = request.form["state"]
        soil_type = request.form["soil_type"]

        location = Location(longitude=longtitude, latitude=latitude)
        applicant = Applicant(first_name=first_name, last_name=last_name, iin=iin, phone_number=phone_number)
        land_plot = LandPlot(area=area, location=location, state=state, soil_type=soil_type)
        queue_request = QueueRequest(document_hash=document_hash, land=land_plot, applicant=applicant)
        queue_service.enqueue(queue_request.to_dict())
        return redirect(url_for("queue_index"))
    return render_template("queue/index.html")


@app.route("/dequeue", methods=["POST"])
def dequeue():
    pass


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text = request.form["text"]
        if len(text) < 1:
            return redirect(url_for("index"))

        make_proof = request.form.get("make_proof", False)
        service.write_block(text, make_proof)
        return redirect(url_for("index"))
    return render_template("index.html")


@app.route("/check", methods=["POST"])
def integrity():
    results = service.check_blocks_integrity()
    print(results)
    if request.method == "POST":
        return render_template("index.html", results=results)
    return render_template("index.html")


@app.route("/mining", methods=["POST"])
def mining():
    if request.method == "POST":
        max_index = int(service.get_next_index())
        print(max_index)
        for i in range(2, max_index):
            service.get_pow(i)
        return render_template("index.html", querry=max_index)
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
