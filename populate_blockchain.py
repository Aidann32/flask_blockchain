import hashlib
import os

from models.queue import Location, LandPlot, QueueRequest, Applicant
from service.queue import QueueService

from faker import Faker
import random


class IINProvider:
    def __init__(self, faker):
        self.faker = faker

    def iin(self):
        # Generate random digits for the IIN
        iin_digits = [random.randint(0, 9) for _ in range(10)]

        # Calculate the checksum
        checksum = ((
            1 * int(iin_digits[0]) + 2 * int(iin_digits[1]) +
            3 * int(iin_digits[2]) + 4 * int(iin_digits[3]) +
            5 * int(iin_digits[4]) + 6 * int(iin_digits[5]) +
            7 * int(iin_digits[6]) + 8 * int(iin_digits[7]) +
            9 * int(iin_digits[8])
        ) % 11) % 10

        # Set the last digit to be the checksum
        iin_digits[9] = checksum

        # Return the generated IIN as a string
        return ''.join(map(str, iin_digits))


class KazakhstanRegionProvider:
    def __init__(self, faker):
        self.faker = faker

    def kazakhstan_region(self):
        regions = [
            'almaty', 'aqtobe', 'astana', 'atyrau', 'east_kazakhstan',
            'jambyl', 'west_kazakhstan', 'karagandy', 'kostanay',
            'kyzylorda', 'mangystau', 'pavlodar', 'north_kazakhstan',
            'turkistan'
        ]
        return self.faker.random_element(regions)


SOIL_TYPES = [
    'forest_steppe',
    'steppe',
    'desert_steppe',
    'desert'
]


def _generate_random_hash() -> str:
    random_bytes = os.urandom(16)
    hash_object = hashlib.md5(random_bytes)
    hash_hex = hash_object.hexdigest()
    return hash_hex


def populate_blockchain(queue_service: QueueService) -> None:
    fake = Faker()
    fake.add_provider(IINProvider)
    fake.add_provider(KazakhstanRegionProvider)
    for i in range(10):
        first_name = fake.first_name()
        last_name = fake.last_name()
        iin = fake.iin()
        phone_number = fake.phone_number()
        longitude = random.uniform(0, 100)
        latitude = random.uniform(0, 100)
        area = random.uniform(100, 1000)
        state = fake.kazakhstan_region()
        soil_type = random.choice(SOIL_TYPES)
        location = Location(longitude=longitude, latitude=latitude)
        applicant = Applicant(first_name=first_name, last_name=last_name, iin=iin, phone_number=phone_number)
        land_plot = LandPlot(area=area, location=location, state=state, soil_type=soil_type)
        place = queue_service.place + 1
        queue_request = QueueRequest(document_hash=_generate_random_hash(), land=land_plot, applicant=applicant, place=place, removed_at=None)
        queue_service.enqueue(queue_request.to_dict())
