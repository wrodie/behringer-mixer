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
    info_address: str = "/xinfo"
    subscription_string: str = "/xremote"
    subscription_renew_string: str = "/renew"

    # input_padding - use automatic if not specified
    # output_padding - use 0 if not specified

    addresses_to_load = [
        {
            "input": "/xinfo",
            "output": "/status",
        },
        # Channels
        {
            "tag": "channels",
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
            "tag": "channels",
            "input": "/ch/{num_channel}/mix/on",
            "output": "/ch/{num_channel}/mix_on",
            "data_type": "boolean",
        },
        {
            "tag": "channels",
            "input": "/ch/{num_channel}/config/name",
            "output": "/ch/{num_channel}/config_name",
        },
        {
            "tag": "channels",
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
            "tag": "channelsends",
            "input": "/ch/{num_channel}/mix/{num_bus}/on",
            "input_padding": {
                "num_bus": 2,
            },
            "output": "/chsend/{num_channel}/{num_bus}/mix_on",
            "data_type": "boolean",
        },
        {
            "tag": "channelsends",
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
            "tag": "auxins",
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
            "tag": "auxins",
            "input": "/auxin/{num_auxin}/mix/on",
            "input_padding": {"num_auxin": 2},
            "output": "/auxin/{num_auxin}/mix_on",
            "data_type": "boolean",
        },
        {
            "tag": "auxins",
            "input": "/auxin/{num_auxin}/config/name",
            "input_padding": {"num_auxin": 2},
            "output": "/auxin/{num_auxin}/config_name",
        },
        {
            "tag": "auxins",
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
            "tag": "busses",
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
            "tag": "busses",
            "input": "/bus/{num_bus}/mix/on",
            "output": "/bus/{num_bus}/mix_on",
            "data_type": "boolean",
        },
        {
            "tag": "busses",
            "input": "/bus/{num_bus}/config/name",
            "output": "/bus/{num_bus}/config_name",
        },
        {
            "tag": "busses",
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
            "tag": "bussends",
            "input": "/bus/{num_bus}/mix/{num_matrix}/on",
            "input_padding": {"num_matrix": 2},
            "output": "/bussend/{num_bus}/{num_matrix}/mix_on",
            "data_type": "boolean",
        },
        {
            "tag": "bussends",
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
            "tag": "matrices",
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
            "tag": "matrices",
            "input": "/mtx/{num_matrix}/mix/on",
            "output": "/mtx/{num_matrix}/mix_on",
            "input_padding": {"num_matrix": 2},
            "data_type": "boolean",
        },
        {
            "tag": "matrices",
            "input": "/mtx/{num_matrix}/config/name",
            "output": "/mtx/{num_matrix}/config_name",
            "input_padding": {"num_matrix": 2},
        },
        {
            "tag": "matrices",
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
            "tag": "dcas",
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
            "tag": "dcas",
            "input": "/dca/{num_dca}/on",
            "output": "/dca/{num_dca}/mix_on",
            "data_type": "boolean",
        },
        {
            "tag": "dcas",
            "input": "/dca/{num_dca}/config/name",
            "output": "/dca/{num_dca}/config_name",
        },
        {
            "tag": "dcas",
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
            "tag": "headamps",
            "input": "/headamp/{num_head_amp}/gain",
            "input_indexing": {"num_head_amp": 0},
            "data_type": "linf",
            "data_type_config": {
                "min": -12.000,
                "max": 60.000,
                "step": 0.500,
            },
            "secondary_output": {
                "_db": {
                    "forward_function": "linf_to_db",
                    "reverse_function": "db_to_linf",
                },
            },
        },
        {
            "tag": "headamps",
            "input": "/headamp/{num_head_amp}/phantom",
            "input_indexing": {"num_head_amp": 0},
            "data_type": "boolean",
        },
        # Mains
        {
            "tag": "mains",
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
            "tag": "mains",
            "input": "/main/st/mix/on",
            "output": "/main/st/mix_on",
            "data_type": "boolean",
        },
        {
            "tag": "mains",
            "input": "/main/st/config/name",
            "output": "/main/st/config_name",
        },
        {
            "tag": "mains",
            "input": "/main/st/config/color",
            "output": "/main/st/config_color",
            "secondary_output": {
                "_name": {
                    "forward_function": "color_index_to_name",
                    "reverse_function": "color_name_to_index",
                },
            },
        },
        # Show
        {
            "tag": "show",
            "input": "/-show/showfile/show/name",
            "output": "/show/name",
        },
        {
            "tag": "show",
            "input": "/-show/prepos/current",
            "output": "/scene/current",
        },
        # USB
        {
            "tag": "usb",
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
            "tag": "usb",
            "input": "/-stat/tape/file",
            "output": "/usb/file",
        },
        {
            "tag": "usb",
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

    def __init__(self, **kwargs):
        """Initialize the XAir mixer"""

        print("XAir")
        self.extra_addresses_to_load = [
            # Mains
            {
                "tag": "mains",
                "input": "/lr/mix/fader",
                "output": "/main/st/mix_fader",
                "secondary_output": {
                    "_db": {
                        "forward_function": "fader_to_db",
                        "reverse_function": "db_to_fader",
                    },
                },
            },
            {
                "tag": "mains",
                "input": "/lr/mix/on",
                "output": "/main/st/mix_on",
                "data_type": "boolean",
            },
            {
                "tag": "mains",
                "input": "/lr/config/name",
                "output": "/main/st/config_name",
            },
            {
                "tag": "mains",
                "input": "/lr/config/color",
                "output": "/main/st/config_color",
                "secondary_output": {
                    "_name": {
                        "forward_function": "color_index_to_name",
                        "reverse_function": "color_name_to_index",
                    },
                },
            },
            {
                "tag": "show",
                "input": "/-snap/index",
                "output": "/scene/current",
            },
            {
                "tag": "bussends",
                "input": "/ch/{num_channel}/mix/{num_bus}/grpon",
                "input_padding": {
                    "num_bus": 2,
                },
                "output": "/chsend/{num_channel}/{num_bus}/mix_on",
                "data_type": "boolean",
            },
            # Headamps
            {
                "tag": "headamps",
                "input": "/headamp/{num_head_amp}/gain",
                "input_padding": {
                    "num_head_amp": 2,
                },
            },
            {
                "tag": "headamps",
                "input": "/headamp/{num_head_amp}/phantom",
                "input_padding": {
                    "num_head_amp": 2,
                },
                "data_type": "boolean",
            },
        ]
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

    def __init__(self, **kwargs):
        """Initialize the X32 mixer"""
        self.extra_addresses_to_load = [
            # Monos
            {
                "tag": "mono",
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
                "tag": "mono",
                "input": "/main/m/mix/on",
                "output": "/main/m/mix_on",
                "data_type": "boolean",
            },
            {
                "tag": "mono",
                "input": "/main/m/config/name",
                "output": "/main/m/config_name",
            },
            {
                "tag": "mono",
                "input": "/main/m/config/color",
                "output": "/main/m/config_color",
                "secondary_output": {
                    "_name": {
                        "forward_function": "color_index_to_name",
                        "reverse_function": "color_name_to_index",
                    },
                },
            },
        ]
        super().__init__(**kwargs)


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


class MixerTypeWING(MixerTypeBase):
    """Class for Behringer Wing Mixer"""

    port_number: int = 2223
    mixer_type: str = "Wing"
    #num_channel: int = 48
    num_channel: int = 1
    #num_bus: int = 16
    num_bus: int = 1
    #num_dca: int = 16
    num_dca: int = 1
    num_fx: int = 8
    #num_auxin: int = 8
    num_auxin: int = 1
    #num_auxrtn: int = 8
    num_auxrtn: int = 1
    #num_matrix: int = 8
    num_matrix: int = 1
    has_mono: bool = True
    #num_head_amp: int = 128
    num_head_amp: int = 1
    info_address: str = "/WING?"
    subscription_string: str = "/*s"
    subscription_renew_string: str = "/*s"

    def __init__(self, **kwargs):
        """Initialize the Wing mixer"""
        self.extra_addresses_to_load = [
            {
                "input": "WING?",
                "output": "/status",
            },
            # Channels
            {
                "tag": "channels",
                "input": "/ch/{num_channel}/fdr",
                "output": "/ch/{num_channel}/mix_fader",
                "input_padding": {
                    "num_channel": 1,
                },            
                "data_index": 1,
                "secondary_output": {
                    "_db": {
                        "data_index": 0,
                    },
                },
            },
            {
                "tag": "channels",
                "input": "/ch/{num_channel}/mute",
                "output": "/ch/{num_channel}/mix_on",
                "data_type": "boolean_inverted",
                "data_index": 2,
            },
            {
                "tag": "channels",
                "input": "/ch/{num_channel}/$name",
                "output": "/ch/{num_channel}/config_name",
            },
            {
                "tag": "channels",
                "input": "/ch/{num_channel}/$col",
                "output": "/ch/{num_channel}/config_color",
                "secondary_output": {
                    "_name": {
                        "data_index": 0,
                        "forward_function": "wing_color_index_to_name",
                        "reverse_function": "wing_color_name_to_index",
                    },
                },
            },
        ]
        super().__init__(**kwargs)


_supported_mixers = [
    "X32",
    "XR18",
    "XR16",
    "XR12",
    "WING",
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
