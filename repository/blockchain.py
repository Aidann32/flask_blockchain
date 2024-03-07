class BlockchainRepository:
    def __init__(self, repos):
        self.repository = repos

    def get_hash(self):
        pass

    def get_block(self):
        pass

    def get_POW(self):
        pass

    def write_block(self):
        pass

# def get_hash(file_name):
#     file_name = str(file_name)
#     if not file_name.endswith(".json"):
#         file_name += ".json"
#     try:
#         with open(BLOCKCHAIN_DIR + file_name, "rb") as file:
#             return hashlib.sha256(file.read()).hexdigest()
#     except Exception:
#         print(f"File {file_name} is not found")
#         raise

# def get_next_block():
#     files = os.listdir(BLOCKCHAIN_DIR)
#     index_list = [int(file.split(".")[0]) for file in files]
#     cur_index = sorted(index_list)[-1]
#     next_index = cur_index + 1
#     return str(next_index)


# def get_POW(file_name, difficulty=1):
#     # POW - proof of work
#     file_name = str(file_name)
#     if file_name.endswith(".json"):
#         file_name = int(file_name.split(".")[0])
#     else:
#         file_name = int(file_name)
#
#     last_proof = json.load(open(BLOCKCHAIN_DIR + str(file_name - 1) + ".json"))["proof"]
#     proof = 0
#     while is_valid_proof(last_proof, proof, difficulty) is False:
#         proof += 1
#     cur_block = json.load(open(BLOCKCHAIN_DIR + str(file_name) + ".json"))
#     cur_block["proof"] = proof
#     cur_block["prev_hash"] = get_hash(str(file_name - 1))
#     with open(BLOCKCHAIN_DIR + str(file_name) + ".json", "w") as file:
#         json.dump(cur_block, file, indent=4, ensure_ascii=False)

# def write_block(text, make_proof=False):
#     cur_index = get_next_block()
#     prev_index = str(int(cur_index) - 1)
#     prev_block_hash = get_hash(prev_index)
#     data = {
#         "text": text,
#         "prev_hash": prev_block_hash,
#         "timestamp": time(),
#         "proof": -1,
#         "index": cur_index,
#     }
#
#     with open(f"{BLOCKCHAIN_DIR}{cur_index}.json", "w") as file:
#         json.dump(data, file, indent=4, ensure_ascii=False)
#     if make_proof:
#         get_POW(str(cur_index))