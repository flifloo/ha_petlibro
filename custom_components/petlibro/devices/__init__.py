from typing import Dict, Type
from .device import Device
from .feeders.granary_feeder import GranaryFeeder
from .feeders.granary_camera_feeder import GranaryCameraFeeder

product_name_map : Dict[str, Type[Device]] = {
    "Granary Feeder": GranaryFeeder,
    "Granary Camera Feeder": GranaryCameraFeeder
}

product_id_map: Dict[str, Type[Device]] = {
    "PLAF103": GranaryFeeder,
    "PLAF203": GranaryCameraFeeder
}
