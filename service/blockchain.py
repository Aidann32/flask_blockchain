import hashlib
import json
import os
from time import time


class BlockchainService:
    def __init__(self, repository):
        self.repository = repository
        self.last_block_index = 0

    def check_blocks_integrity(self) -> list:
        result = []
        cur_proof = -1
        for i in range(2, int(self.get_next_index())):
            prev_index = str(i - 1)
            cur_index = str(i)
            tmp = {
                "block": "",
                "result": "",
                "proof": ""
            }
            try:
                block = self.repository.get_block(cur_index)
                cur_hash = block["prev_hash"]
                cur_proof = block["proof"]
            except Exception as e:
                print(e)

            try:
                prev_hash = hashlib.sha256(
                    str(self.repository.get_block(prev_index)).encode("utf-8")
                ).hexdigest()
            except Exception as e:
                print(e)

            tmp["block"] = prev_index
            tmp["proof"] = cur_proof
            if cur_hash == prev_hash:
                tmp["result"] = "ok"
            else:
                tmp["result"] = "error"
            result.append(tmp)
        return result

    def check_block(self, index: int) -> dict:
        cur_index = str(index)
        prev_index = str(int(index) - 1)
        cur_proof = -1
        cur_hash = 0
        prev_hash = 0
        tmp = {
            "block": "",
            "result": "",
            "proof": ""
        }
        try:
            block = self.repository.get_block(cur_index)
            cur_hash = block["prev_hash"]
            cur_proof = block["proof"]
        except Exception as e:
            print(e)

        try:
            prev_hash = hashlib.sha256(
                str(self.repository.get_block(prev_index)).encode("utf-8")
            ).hexdigest()
        except Exception as e:
            print(e)

        tmp["block"] = prev_index
        tmp["proof"] = cur_proof
        if cur_hash == prev_hash:
            tmp["result"] = "ok"
        else:
            tmp["result"] = "error"
        return tmp

    def get_hash(self, index: str) -> str:
        try:
            return hashlib.sha256(str(self.repository.get_block(index)).encode("utf-8")).hexdigest()
        except Exception:
            print("Error!")
            raise

    def is_valid_proof(self, last_proof: str, proof: int, difficulty: int):
        guess = f"{last_proof}{proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty] == "0" * difficulty

    def get_pow(self, index: int, difficulty=1) -> None:
        # POW - proof of work
        last_proof = self.repository.get_block(index)["proof"]
        proof = 0
        while self.is_valid_proof(last_proof, proof, difficulty) is False:
            proof += 1
        cur_block = self.repository.get_block(index)
        cur_block["proof"] = proof
        cur_block["prev_hash"] = self.get_hash(str(index - 1))
        self.repository.set_proof(cur_block)

    def get_next_index(self):
        return self.last_block_index + 1

    def write_block(self, data: str, make_proof=False):
        cur_index = self.get_next_index()
        prev_index = str(int(cur_index) - 1)
        prev_block_hash = self.get_hash(prev_index)
        data_ = {
            "text": data,
            "prev_hash": prev_block_hash,
            "timestamp": time(),
            "proof": -1,
            "index": cur_index,
        }
        try:
            self.repository.write_block(cur_index, data_)
            self.last_block_index += 1
            if make_proof:
                self.get_pow(cur_index)
        except Exception as e:
            print(e)
