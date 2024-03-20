from service.blockchain import BlockchainService


class QueueService:
    def __init__(self, blockchain_service: BlockchainService):
        self.blockchain_service = blockchain_service
        self.place = 0

    def enqueue(self, data: dict) -> None:
        # Validation
        self.place += 1
        self.blockchain_service.write_block(data, True)

    def dequeue(self):
        last_index = self.blockchain_service.get_last_index()
        result = self.blockchain_service.get_block(last_index)

        # self.blockchain_service.delete_block(last_index)
        return result

    def find_key_by_document_hash(self, document_hash: str) -> dict:
        return self.blockchain_service.find_key_by_document_hash(document_hash)
