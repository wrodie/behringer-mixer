from .mixer_type_base import MixerTypeBase


class MixerTypeXSeriesBase(MixerTypeBase):
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
        # Mute Groups
        {
            "tag": "mutegroups",
            "input": "/config/mute/{num_mute_groups}",
            "output": "/mutegroups/{num_mute_groups}/on",
            "data_type": "boolean",
        },
    ]

    cmd_scene_load = "/-action/goscene"
