import hashlib
import json
from redis import Redis


class RedisRepository:
    def __init__(self, redis: Redis):
        self.redis = redis

    def get_hash(self, block_index: int):
        block_index = str(block_index)
        block = str(self.redis.hgetall(block_index))
        if not block:
            print("Block not found")
            raise KeyError("Block not found")
        return hashlib.sha256(block.encode("utf-8")).hexdigest()

    def get_next_block(self, last_index: str):
        last_block = str(self.redis.hgetall(last_index))
        if not last_block:
            print("Block not found")
            raise KeyError("Block not found")
        return last_block

    def get_block(self, block_index: str) -> dict:
        data = self.redis.get(block_index)
        return json.loads(data)

    def set_proof(self, block: str, index: str):
        self.redis.set(index, block)

    def write_block(self, next_index: str,  data: str):
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
        keys = self.redis.keys()
        for key in keys:
            data_str = self.redis.get(key)
            data = json.loads(data_str)
            print(data)
            request_data = data.get('data')
            if request_data.get('document_hash') == document_hash:
                return key.decode('utf-8')

        return dict()
