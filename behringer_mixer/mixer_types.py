import sys
from .mixer_base import MixerBase


class MixerTypeBase(MixerBase):
    """Base class for mixer type configuration"""

    mixer_type: str = ""
    port_number: int = 10023
    delay: float = 0.002
    num_channel: int = 0
    num_bus: int = 0
    num_dca: int = 0
    num_fx: int = 0
    num_auxin: int = 0
    num_auxrtn: int = 0
    num_matrix: int = 0
    num_scenes: int = 100

    addresses_to_load = [
        ["/xinfo", "/status"],
        ["/ch/{num_channel}/mix/fader"],
        ["/ch/{num_channel}/mix/on"],
        ["/ch/{num_channel}/config/name"],
        [
            "/ch/{num_channel}/mix/{num_bus}/on",
            "/chsend/{num_channel}/{num_bus}/mix/on",
        ],
        [
            "/ch/{num_channel}/mix/{num_bus}/level",
            "/chsend/{num_channel}/{num_bus}/mix/fader",
        ],
        ["/auxin/{num_auxin:2}/mix/fader"],
        ["/auxin/{num_auxin:2}/mix/on"],
        ["/auxin/{num_auxin:2}/config/name"],
        ["/bus/{num_bus}/mix/fader"],
        ["/bus/{num_bus}/mix/on"],
        ["/bus/{num_bus}/config/name"],
        [
            "/bus/{num_bus}/mix/{num_matrix:2}/on",
            "/bussend/{num_bus}/{num_matrix:2}/mix/on",
        ],
        [
            "/bus/{num_bus}/mix/{num_matrix:2}/level",
            "/bussend/{num_bus}/{num_matrix:2}/mix/fader",
        ],
        ["/mtx/{num_matrix:2}/mix/fader"],
        ["/mtx/{num_matrix:2}/mix/on"],
        ["/mtx/{num_matrix:2}/config/name"],
        ["/dca/{num_dca}/fader", "/dca/{num_dca}/mix/fader"],
        ["/dca/{num_dca}/on", "/dca/{num_dca}/mix/on"],
        ["/dca/{num_dca}/config/name"],
        ["/main/st/mix/fader"],
        ["/main/st/mix/on"],
        ["/main/st/config/name"],
        ["/-show/showfile/show/name", "/show/name"],
        ["/-show/prepos/current", "/scene/current"],
        ["/-stat/tape/state", "/usb/state", {0: "STOP", 1: "PAUSE", 2: "PLAY", 3: "PAUSE_RECORD", 4: "RECORD", 5: "FAST_FORWARD", 6: "REWIND"}],
        ["/-stat/tape/file", "/usb/file"],
        ["/-stat/usbmounted", "/usb/mounted"],
    ]

    cmd_scene_load = "/-action/goscene"

    def info(self):
        """Return information about the mixer"""
        return {
            "channel": {
                "number": self.num_channel,
                "base_address": "ch",
            },
            "bus": {
                "number": self.num_bus,
                "base_address": "bus",
            },
            "matrix": {
                "number": self.num_matrix,
                "base_address": "mtx",
            },
            "dca": {
                "number": self.num_dca,
                "base_address": "dca",
            },
            "fx": {
                "number": self.num_fx,
                "base_address": "fx",
            },
            "auxin": {
                "number": self.num_auxin,
                "base_address": "auxin",
            },
            "auxrtn": {
                "number": self.num_auxrtn,
                "base_address": "auxrtn",
            },
            "scenes": {
                "number": self.num_scenes,
                "base_address": "scene",
            },
            "channel_sends": {
                "number": 0,
                "base_address": "chsend",
            },
            "bus_sends": {
                "number": 0,
                "base_address": "bussend",
            },
        }


class MixerTypeXAir(MixerTypeBase):
    """Base Mixer class for the XAir type mixers"""

    port_number: int = 10024

    cmd_scene_load = "/-snap/load"

    extra_addresses_to_load = [
        ["/lr/mix/fader", "/main/st/mix/fader"],
        ["/lr/mix/on", "/main/st/mix/on"],
        ["/lr/config/name", "/main/st/config/name"],
        ["/-snap/index", "/scene/current"],
        [
            "/ch/{num_channel}/mix/{num_bus}/grpon",
            "/chsend/{num_channel}/{num_bus}/mix/on",
        ],
    ]

    def __init__(self, **kwargs):
        self.addresses_to_load += self.extra_addresses_to_load
        super().__init__(**kwargs)


class MixerTypeX32(MixerTypeBase):
    """Class for Behringer X32 Mixer"""

    mixer_type: str = "X32"
    num_channel: int = 32
    num_bus: int = 16
    num_dca: int = 8
    num_fx: int = 8
    num_auxin: int = 8
    num_auxrtn: int = 8
    num_matrix: int = 6


class MixerTypeXR12(MixerTypeXAir):
    """Class for Behringer XR-12 Mixer"""

    mixer_type: str = "XR12"
    num_channel: int = 12
    num_bus: int = 2
    num_dca: int = 4
    num_fx: int = 4


class MixerTypeXR16(MixerTypeXAir):
    """Class for Behringer XR-16 Mixer"""

    mixer_type: str = "XR16"
    num_channel: int = 16
    num_bus: int = 4
    num_dca: int = 4
    num_fx: int = 4


class MixerTypeXR18(MixerTypeXAir):
    """Class for Behringer XR-18 Mixer"""

    mixer_type: str = "XR18"
    num_channel: int = 16
    num_bus: int = 6
    num_dca: int = 4
    num_fx: int = 4
    num_auxrtn: int = 2


_supported_mixers = [
    "X32",
    "XR18",
    "XR16",
    "XR12",
]


def make_mixer(mixer_type, **kwargs):
    """Make the actual mixer object based on the type"""
    if mixer_type in _supported_mixers:
        mixer_class_name = "MixerType" + mixer_type
        module_ = sys.modules[__name__]
        mixer_class = getattr(module_, mixer_class_name)
        mixer_object = mixer_class(**kwargs)
        return mixer_object
    return None
