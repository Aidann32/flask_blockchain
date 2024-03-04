from flask import Flask
import redis

from repository.redis.repository import RedisRepository

app = Flask(__name__, template_folder='web_service/templates')
storage = redis.Redis(host='localhost', port=6379, decode_responses=True)

r = RedisRepository(storage)

if __name__ == "__main__":
    app.run(debug=True)
