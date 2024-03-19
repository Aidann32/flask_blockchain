from flask import Blueprint, request, render_template, redirect, url_for

import hashlib

from app import queue_service
from utils.utils import extract_text_from_docx
from models.queue import *

queue_blueprint = Blueprint('queue', __name__, template_folder='web_service/templates')


@queue_blueprint.route("/", methods=["GET"])
def queue_main():
    return render_template("queue/index.html")


@queue_blueprint.route("/request", methods=["GET", "POST"])
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


@queue_blueprint.route("/search", methods=["GET", "POST"])
def search_request():
    if request.method == "POST":
        document_hash = request.form["document_hash"]
        request_block = queue_service.find_key_by_document_hash(document_hash)
        return render_template("queue/search_request.html", request_block=request_block)
    return render_template("queue/search_request.html")


@queue_blueprint.route("/dequeue", methods=["POST"])
def dequeue():
    pass

@queue_blueprint.route("/queue_view", methods=["GET", "POST"])
def queue_view():
    pass

