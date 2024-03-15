from dataclasses import dataclass, asdict
from datetime import date

@dataclass
class Location:
    longitude: float
    latitude: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Applicant:
    first_name: str
    last_name: str
    iin: str
    phone_number: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class LandPlot:
    area: float
    location: Location
    state: str
    soil_type: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class QueueRequest:
    land: LandPlot
    applicant: Applicant
    document_hash: str
    place: int
    removed_at: date

    def to_dict(self) -> dict:
        return asdict(self)
