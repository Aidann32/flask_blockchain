from service.blockchain import BlockchainService


class QueueService:
    def __init__(self, blockchain_service: BlockchainService, removed_requests_blockchain_service: BlockchainService):
        self.blockchain_service = blockchain_service
        self.removed_requests_blockchain_service = removed_requests_blockchain_service

    def _does_exist(self, iin: str) -> bool:
        return self.blockchain_service.does_exist(iin)

    def find_last_request_key(self) -> str:
        return self.blockchain_service.find_last_request_key()

    def enqueue(self, data: dict) -> bool:
        iin = data.get('applicant', {}).get('iin')
        if not self._does_exist(iin):
            self.blockchain_service.write_block(data, rtype="request", make_proof=True)
            return True
        return False

    def dequeue(self, document_hash: str) -> bool:
        last_index = self.find_last_request_key()
        request = self.blockchain_service.get_block(int(last_index))
        if request.get('data', {}).get('document_hash', {}) == document_hash:
            self.removed_requests_blockchain_service.write_block(request.get('data'), rtype="removed", make_proof=True)
            return True
        return False

    def find_key_by_document_hash(self, document_hash: str) -> dict:
        requests = self.blockchain_service.find_key_by_document_hash(document_hash)
        if not requests:
            return self.removed_requests_blockchain_service.find_key_by_document_hash(document_hash)
        return requests
