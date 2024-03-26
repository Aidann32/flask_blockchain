import hashlib
import json
from redis import Redis
from datetime import datetime


class RedisRepository:
    def __init__(self, redis: Redis):
        self.redis = redis

    def get_hash(self, block_index: int):
        block_index = str(block_index)
        block = str(self.redis.hgetall(block_index))
        if not block:
            raise KeyError("Block not found")
        return hashlib.sha256(block.encode("utf-8")).hexdigest()

    def get_next_block(self, last_index: str):
        last_block = str(self.redis.hgetall(last_index))
        if not last_block:
            raise KeyError("Block not found")
        return last_block

    def get_block(self, block_index: str) -> dict:
        data = self.redis.get(block_index)
        return json.loads(data)

    def set_proof(self, block: str, index: str):
        self.redis.set(index, block)

    def write_block(self, next_index: str, data: str):
        self.redis.set(next_index, data)

    def delete_all_keys(self):
        keys = self.redis.keys()
        if keys:
            self.redis.delete(*keys)

    def get_all_blocks(self) -> dict:
        keys = self.redis.keys()
        result = {}
        for key in keys:
            value = self.redis.get(key)
            try:
                result[key] = json.loads(value)
            except json.JSONDecodeError:
                result[key] = value

        return result

    def find_key_by_document_hash(self, document_hash: str) -> dict:
        keys = self.redis.keys('*')
        for key in keys:
            data_str = self.redis.get(key)
            data = json.loads(data_str)
            if 'data' in data.keys():
                if data['data'].get('document_hash') == document_hash:
                    return data['data']

        return dict()

    def does_exist(self, iin: str):
        keys = self.redis.keys()

        for key in keys:
            data = self.redis.get(key)
            data_dict = json.loads(data)
            if data_dict.get('data', {}).get('applicant', {}).get('iin') == iin:
                return True

        return False

    def find_last_request_key(self) -> str:
        keys = self.redis.keys()
        result = ""
        created_at = datetime.now()
        for key in keys:
            data = self.redis.get(key)
            data_dict = json.loads(data)
            timestamp = data_dict.get('timestamp', {})
            if timestamp:
                created_at_request = datetime.fromtimestamp(timestamp)
                if created_at > created_at_request:
                    created_at = created_at_request
                    result = key

        return result
