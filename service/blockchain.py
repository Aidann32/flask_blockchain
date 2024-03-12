import hashlib
import json
from time import time


class BlockchainService:
    def __init__(self, repository, logger):
        self.repository = repository
        self.last_block_index = 0
        self.repository.delete_all_keys()
        self._write_genesis_block()
        self.logger = logger

    def get_last_index(self) -> int:
        if self.last_block_index == 0:
            return None
        return self.last_block_index

    def check_blocks_integrity(self) -> list:
        self.logger.info("Checking blocks integrity started")
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
                self.logger.error(e)

            try:
                prev_hash = hashlib.sha256(
                    str(self.repository.get_block(prev_index)).encode("utf-8")
                ).hexdigest()
            except Exception as e:
                self.logger.error(e)

            tmp["block"] = prev_index
            tmp["proof"] = cur_proof
            if cur_hash == prev_hash:
                tmp["result"] = "ok"
                self.logger.info("Integrity check passed")
            else:
                tmp["result"] = "error"
                self.logger.info("Integrity check failed")
            result.append(tmp)

        return result

    def check_block(self, index: int) -> dict:
        self.logger.info(f"Checking block at index [{index}] started")
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
            self.logger.error(e)

        try:
            prev_hash = hashlib.sha256(
                str(self.repository.get_block(prev_index)).encode("utf-8")
            ).hexdigest()
        except Exception as e:
            self.logger.error(e)

        tmp["block"] = prev_index
        tmp["proof"] = cur_proof
        if cur_hash == prev_hash:
            tmp["result"] = "ok"
            self.logger.info(f"Check block at index [{index}] passed")
        else:
            tmp["result"] = "error"
            self.logger.info(f"Check block at index [{index}] failed")
        return tmp

    def get_hash(self, index: str) -> str:
        try:
            return hashlib.sha256(str(self.repository.get_block(index)).encode("utf-8")).hexdigest()
        except Exception:
            print("Error!")
            raise

    def is_valid_proof(self, last_proof: str, proof: int, difficulty: int) -> bool:
        self.logger.info(f"Validating proof. Inputs: {last_proof}, {proof}, {difficulty}")
        guess = f"{last_proof}{proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty] == "0" * difficulty

    def get_pow(self, index: int, difficulty=1) -> None:
        # POW - proof of work
        self.logger.info(f"Getting proof of work at index [{index}]")
        last_proof = self.repository.get_block(index)["proof"]
        proof = 0
        while self.is_valid_proof(last_proof, proof, difficulty) is False:
            proof += 1
        cur_block = self.repository.get_block(index)
        cur_block["proof"] = proof
        cur_block["prev_hash"] = self.get_hash(str(index - 1))
        self.logger.info(f"get_pow {cur_block}")
        cur_block = json.dumps(cur_block)
        self.repository.set_proof(cur_block, str(index))

    def get_next_index(self) -> int:
        return self.last_block_index + 1

    def write_block(self, data: [str, dict], make_proof=False) -> None:
        self.logger.info(f"Writing block {data}")
        cur_index = self.get_next_index()
        prev_index = str(int(cur_index) - 1)
        prev_block_hash = self.get_hash(prev_index)
        data_ = {
            "data": data,
            "prev_hash": prev_block_hash,
            "timestamp": time(),
            "proof": -1,
            "index": cur_index,
        }
        data_ = json.dumps(data_)
        try:
            self.repository.write_block(cur_index, data_)
            self.last_block_index += 1
            if make_proof:
                self.get_pow(cur_index)
        except Exception as e:
            self.logger.error(e)

    def delete_block(self, index: int) -> None:
        self.repository.delete_block(index)

    def get_block(self, index: int) -> dict:
        return self.repository.get_block(str(index))

    def _write_genesis_block(self) -> None:
        data_ = {
            "text": "Genesis",
            "prev_hash": 0,
            "timestamp": time(),
            "proof": -1,
            "index": 0,
        }
        data_ = json.dumps(data_)
        self.repository.write_block(0, data_)
