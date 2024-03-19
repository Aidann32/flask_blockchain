from flask import Blueprint, request, render_template, redirect, url_for

from app import demo_service


blockchain_blueprint = Blueprint('blockchain', __name__)


@blockchain_blueprint.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text = request.form["text"]
        if len(text) < 1:
            return redirect(url_for("index"))

        make_proof = request.form.get("make_proof", False)
        demo_service.write_block(text, make_proof)
        return redirect(url_for("index"))
    return render_template("blockchain/index.html")


@blockchain_blueprint.route("/check", methods=["POST"])
def integrity():
    results = demo_service.check_blocks_integrity()
    if request.method == "POST":
        return render_template("blockchain/index.html", results=results)
    return render_template("blockchain/index.html")


@blockchain_blueprint.route("/mining", methods=["POST"])
def mining():
    if request.method == "POST":
        max_index = int(demo_service.get_next_index())
        for i in range(2, max_index):
            demo_service.get_pow(i)
        return render_template("blockchain/index.html", querry=max_index)
    return render_template("blockchain/index.html")


