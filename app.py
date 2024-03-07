from flask import Flask
import redis
from flask import render_template, redirect, url_for
from flask import request

import config
from repository.redis.repository import RedisRepository
from repository.file_storage.repository import FileRepository
from service.blockchain import BlockchainService

app = Flask(__name__, template_folder='web_service/templates')

try:
    storage = redis.Redis(host=config.REDIS_CONFIG['host'], port=config.REDIS_CONFIG['port'], decode_responses=config.REDIS_CONFIG['decode_responses'])
    r = RedisRepository(storage)
except Exception as e:
    r = FileRepository(path_to_folder=config.PATH_TO_FOLDER)
    print(e)

service = BlockchainService(repository=r)


# def cleanup():
#     r.delete_all_keys()
#
#
# @app.teardown_appcontext
# def teardown_appcontext(error=None):
#     cleanup()


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
    if request.method == "POST":
        return render_template("index.html", results=results)
    return render_template("index.html")


@app.route("/mining", methods=["POST"])
def mining():
    if request.method == "POST":
        max_index = int(service.get_next_index())

        for i in range(2, max_index):
            service.get_pow(i)
        return render_template("index.html", querry=max_index)
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
