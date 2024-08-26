from typing import Dict, Type
from .device import Device
from .feeders.granary_feeder import GranaryFeeder
from .feeders.one_rfid_pet_feeder import OneRFIDPetFeeder

product_name_map : Dict[str, Type[Device]] = {
    "Granary Feeder": GranaryFeeder,
    "One RFID Pet Feeder": OneRFIDPetFeeder
}
