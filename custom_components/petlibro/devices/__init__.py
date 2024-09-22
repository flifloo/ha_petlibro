from typing import Dict, Type
from .device import Device
from .feeders.granary_smart_feeder import GranarySmartFeeder
from .feeders.granary_camera_feeder import GranaryCameraFeeder

product_name_map : Dict[str, Type[Device]] = {
    "Granary Smart Feeder": GranarySmartFeeder,
    "Granary Camera Feeder": GranaryCameraFeeder
}
