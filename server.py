from app import app
from web_service.queue import queue_blueprint
from web_service.blockchain import blockchain_blueprint


if __name__ == "__main__":
    app.register_blueprint(queue_blueprint, url_prefix="/queue")
    app.register_blueprint(blockchain_blueprint, url_prefix="/blockchain")
    app.run(debug=True)
