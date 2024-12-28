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
    num_head_amp: int = 0
    has_mono: bool = False

    # input_padding - use automatic if not specified
    # output_padding - use 0 if not specified

    addresses_to_load = [
        {
            "input": "/xinfo",
            "output": "/status",
        },
        # Channels
        {
            "input": "/ch/{num_channel}/mix/fader",
            "output": "/ch/{num_channel}/mix_fader",
            "secondary_output": {
                "_db": {
                    "forward_function": "fader_to_db",
                    "reverse_function": "db_to_fader",
                },
            },
        },
        {
            "input": "/ch/{num_channel}/mix/on",
            "output": "/ch/{num_channel}/mix_on",
            "data_type": "boolean",
        },
        {
            "input": "/ch/{num_channel}/config/name",
            "output": "/ch/{num_channel}/config_name",
        },
        {
            "input": "/ch/{num_channel}/config/color",
            "output": "/ch/{num_channel}/config_color",
            "secondary_output": {
                "_name": {
                    "forward_function": "color_index_to_name",
                    "reverse_function": "color_name_to_index",
                },
            },
        },
        # Channel Sends
        {
            "input": "/ch/{num_channel}/mix/{num_bus}/on",
            "input_padding": {
                "num_bus": 2,
            },
            "output": "/chsend/{num_channel}/{num_bus}/mix_on",
            "data_type": "boolean",
        },
        {
            "input": "/ch/{num_channel}/mix/{num_bus}/level",
            "input_padding": {
                "num_bus": 2,
            },
            "output": "/chsend/{num_channel}/{num_bus}/mix_fader",
            "secondary_output": {
                "_db": {
                    "forward_function": "fader_to_db",
                    "reverse_function": "db_to_fader",
                },
            },
        },
        # Auxins
        {
            "input": "/auxin/{num_auxin}/mix/fader",
            "input_padding": {"num_auxin": 2},
            "output": "/auxin/{num_auxin}/mix_fader",
            "secondary_output": {
                "_db": {
                    "forward_function": "fader_to_db",
                    "reverse_function": "db_to_fader",
                },
            },
        },
        {
            "input": "/auxin/{num_auxin}/mix/on",
            "input_padding": {"num_auxin": 2},
            "output": "/auxin/{num_auxin}/mix_on",
            "data_type": "boolean",
        },
        {
            "input": "/auxin/{num_auxin}/config/name",
            "input_padding": {"num_auxin": 2},
            "output": "/auxin/{num_auxin}/config_name",
        },
        {
            "input": "/auxin/{num_auxin}/config/color",
            "input_padding": {"num_auxin": 2},
            "output": "/auxin/{num_auxin}/config_color",
            "secondary_output": {
                "_name": {
                    "forward_function": "color_index_to_name",
                    "reverse_function": "color_name_to_index",
                },
            },
        },
        # Busses
        {
            "input": "/bus/{num_bus}/mix/fader",
            "output": "/bus/{num_bus}/mix_fader",
            "secondary_output": {
                "_db": {
                    "forward_function": "fader_to_db",
                    "reverse_function": "db_to_fader",
                },
            },
        },
        {
            "input": "/bus/{num_bus}/mix/on",
            "output": "/bus/{num_bus}/mix_on",
            "data_type": "boolean",
        },
        {
            "input": "/bus/{num_bus}/config/name",
            "output": "/bus/{num_bus}/config_name",
        },
        {
            "input": "/bus/{num_bus}/config/color",
            "output": "/bus/{num_bus}/config_color",
            "secondary_output": {
                "_name": {
                    "forward_function": "color_index_to_name",
                    "reverse_function": "color_name_to_index",
                },
            },
        },
        # Bus Sends
        {
            "input": "/bus/{num_bus}/mix/{num_matrix}/on",
            "input_padding": {"num_matrix": 2},
            "output": "/bussend/{num_bus}/{num_matrix}/mix_on",
            "data_type": "boolean",
        },
        {
            "input": "/bus/{num_bus}/mix/{num_matrix}/level",
            "input_padding": {"num_matrix": 2},
            "output": "/bussend/{num_bus}/{num_matrix}/mix_fader",
            "secondary_output": {
                "_db": {
                    "forward_function": "fader_to_db",
                    "reverse_function": "db_to_fader",
                },
            },
        },
        # Matrices
        {
            "input": "/mtx/{num_matrix}/mix/fader",
            "output": "/mtx/{num_matrix}/mix_fader",
            "input_padding": {"num_matrix": 2},
            "secondary_output": {
                "_db": {
                    "forward_function": "fader_to_db",
                    "reverse_function": "db_to_fader",
                },
            },
        },
        {
            "input": "/mtx/{num_matrix}/mix/on",
            "output": "/mtx/{num_matrix}/mix_on",
            "input_padding": {"num_matrix": 2},
            "data_type": "boolean",
        },
        {
            "input": "/mtx/{num_matrix}/config/name",
            "output": "/mtx/{num_matrix}/config_name",
            "input_padding": {"num_matrix": 2},
        },
        {
            "input": "/mtx/{num_matrix}/config/color",
            "output": "/mtx/{num_matrix}/config_color",
            "input_padding": {"num_matrix": 2},
            "secondary_output": {
                "_name": {
                    "forward_function": "color_index_to_name",
                    "reverse_function": "color_name_to_index",
                },
            },
        },
        # DCAs
        {
            "input": "/dca/{num_dca}/fader",
            "output": "/dca/{num_dca}/mix_fader",
            "secondary_output": {
                "_db": {
                    "forward_function": "fader_to_db",
                    "reverse_function": "db_to_fader",
                },
            },
        },
        {
            "input": "/dca/{num_dca}/on",
            "output": "/dca/{num_dca}/mix_on",
            "data_type": "boolean",
        },
        {
            "input": "/dca/{num_dca}/config/name",
            "output": "/dca/{num_dca}/config_name",
        },
        {
            "input": "/dca/{num_dca}/config/color",
            "output": "/dca/{num_dca}/config_color",
            "secondary_output": {
                "_name": {
                    "forward_function": "color_index_to_name",
                    "reverse_function": "color_name_to_index",
                },
            },
        },
        # Headamps
        {
            "input": "/headamp/{num_head_amp}/gain",
            "input_indexing": {"num_head_amp": 0},
        },
        {
            "input": "/headamp/{num_head_amp}/phantom",
            "input_indexing": {"num_head_amp": 0},
        },
        # Mains
        {
            "input": "/main/st/mix/fader",
            "output": "/main/st/mix_fader",
            "secondary_output": {
                "_db": {
                    "forward_function": "fader_to_db",
                    "reverse_function": "db_to_fader",
                },
            },
        },
        {
            "input": "/main/st/mix/on",
            "output": "/main/st/mix_on",
            "data_type": "boolean",
        },
        {
            "input": "/main/st/config/name",
            "output": "/main/st/config_name",
        },
        {
            "input": "/main/st/config/color",
            "output": "/main/st/config_color",
            "secondary_output": {
                "_name": {
                    "forward_function": "color_index_to_name",
                    "reverse_function": "color_name_to_index",
                },
            },
        },
        # Monos
        {
            "input": "/main/m/mix/fader",
            "output": "/main/m/mix_fader",
            "secondary_output": {
                "_db": {
                    "forward_function": "fader_to_db",
                    "reverse_function": "db_to_fader",
                },
            },
        },
        {
            "input": "/main/m/mix/on",
            "output": "/main/m/mix_on",
            "data_type": "boolean",
        },
        {
            "input": "/main/m/config/name",
            "output": "/main/m/config_name",
        },
        {
            "input": "/main/m/config/color",
            "output": "/main/m/config_color",
            "secondary_output": {
                "_name": {
                    "forward_function": "color_index_to_name",
                    "reverse_function": "color_name_to_index",
                },
            },
        },
        # Show
        {
            "input": "/-show/showfile/show/name",
            "output": "/show/name",
        },
        {
            "input": "/-show/prepos/current",
            "output": "/scene/current",
        },
        # USB
        {
            "input": "/-stat/tape/state",
            "output": "/usb/state",
            "mapping": {
                0: "STOP",
                1: "PAUSE",
                2: "PLAY",
                3: "PAUSE_RECORD",
                4: "RECORD",
                5: "FAST_FORWARD",
                6: "REWIND",
            },
        },
        {
            "input": "/-stat/tape/file",
            "output": "/usb/file",
        },
        {
            "input": "/-stat/usbmounted",
            "output": "/usb/mounted",
        },
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
            "head_amps": {
                "number": self.num_head_amp,
                "base_address": "headamp",
            },
            "has_mono": self.has_mono,
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
            "/ch/{num_channel}/mix/{num_bus:2}/grpon",
            "/chsend/{num_channel}/{num_bus:2}/mix/on",
        ],
        ["/headamp/{num_head_amp:2,1}/gain", "/headamp/{num_head_amp:3,1}/gain"],
        ["/headamp/{num_head_amp:2,1}/phantom", "/headamp/{num_head_amp:3,1}/phantom"],
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
    has_mono: bool = True
    num_head_amp: int = 128


class MixerTypeXR12(MixerTypeXAir):
    """Class for Behringer XR-12 Mixer"""

    mixer_type: str = "XR12"
    num_channel: int = 12
    num_bus: int = 2
    num_dca: int = 4
    num_fx: int = 4
    num_head_amp: int = 4


class MixerTypeXR16(MixerTypeXAir):
    """Class for Behringer XR-16 Mixer"""

    mixer_type: str = "XR16"
    num_channel: int = 16
    num_bus: int = 4
    num_dca: int = 4
    num_fx: int = 4
    num_head_amp: int = 8


class MixerTypeXR18(MixerTypeXAir):
    """Class for Behringer XR-18 Mixer"""

    mixer_type: str = "XR18"
    num_channel: int = 16
    num_bus: int = 6
    num_dca: int = 4
    num_fx: int = 4
    num_auxrtn: int = 2
    num_head_amp: int = 16


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
