from typing import Dict, Type
from .device import Device
from .feeders.granary_feeder import GranaryFeeder

product_name_map : Dict[str, Type[Device]] = {
    "Granary Feeder": GranaryFeeder
}
