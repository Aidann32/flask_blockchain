import hashlib
from time import time
from redis import Redis
from typing import List


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

    def get_block(self, block_index: str):
        return self.redis.hgetall(block_index)

    def set_proof(self, block: dict, index: str):
        self.redis.hset(index, mapping=block)

    def write_block(self, next_index: str,  data: dict):
        print(f"Writing data {data}")
        self.redis.hset(next_index, mapping=data)

    def delete_all_keys(self):
        keys = self.redis.keys()
        if keys:
            self.redis.delete(*keys)
