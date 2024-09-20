from typing import Dict, Type
from .device import Device
from .feeders.granary_feeder import GranaryFeeder
from .feeders.one_rfid_smart_feeder import OneRFIDSmartFeeder


product_name_map : Dict[str, Type[Device]] = {
    "Granary Feeder": GranaryFeeder,
    "One RFID Smart Feeder": OneRFIDSmartFeeder
}
