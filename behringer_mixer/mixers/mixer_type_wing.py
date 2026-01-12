from .mixer_type_base import MixerTypeBase


class MixerTypeWING(MixerTypeBase):
    """Class for Behringer WING Mixer"""

    port_number: int = 2223
    mixer_type: str = "WING"
    num_channel: int = 40
    num_bus: int = 16
    num_bus_send: int = 16
    num_dca: int = 16
    num_fx: int = 0
    num_auxin: int = 8
    num_auxrtn: int = 0
    num_matrix: int = 8
    has_mono: bool = False
    num_head_amp: int = 8
    num_aes50_in: int = 48
    num_mains: int = 4
    num_mute_groups: int = 8
    info_address: str = "/?"
    subscription_string: str = "/*s"
    subscription_renew_string: str = "/*s"

    cmd_scene_load = "/$ctl/lib/$actionidx"
    cmd_scene_execute = ["/$ctl/lib/$action", "GO"]

    def __init__(self, **kwargs):
        self.extra_addresses_to_load = [
            # Mixer info (WING answers "/?" with a "/*" or "/?" response)
            {
                "input": "/?",
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
                "write_transform": "fader_to_db",
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
                "input_padding": {
                    "num_channel": 1,
                },
                "data_type": "boolean_inverted",
                "data_index": 2,
            },
            {
                "tag": "channels",
                "input_padding": {
                    "num_channel": 1,
                },
                "input": "/ch/{num_channel}/$name",
                "output": "/ch/{num_channel}/config_name",
            },
            {
                "tag": "channels",
                "input": "/ch/{num_channel}/$col",
                "output": "/ch/{num_channel}/config_color",
                "input_padding": {
                    "num_channel": 1,
                },
                "data_index": 2,
                "secondary_output": {
                    "_name": {
                        "forward_function": "wing_color_index_to_name",
                        "reverse_function": "wing_color_name_to_index",
                    },
                },
            },
            # Channel Sends
            {
                "tag": "channelsends",
                "input": "/ch/{num_channel}/send/{num_bus}/on",
                "data_index": 2,
                "input_padding": {
                    "num_bus": 1,
                    "num_channel": 1,
                },
                "write_transform": "fader_to_db",
                "output": "/chsend/{num_channel}/{num_bus}/mix_on",
                "data_type": "boolean",
            },
            {
                "tag": "channelsends",
                "input": "/ch/{num_channel}/send/{num_bus}/lvl",
                "input_padding": {
                    "num_bus": 1,
                    "num_channel": 1,
                },
                "output": "/chsend/{num_channel}/{num_bus}/mix_fader",
                "data_index": 1,
                "secondary_output": {
                    "_db": {
                        "data_index": 0,
                    },
                },
            },
            # Auxins
            {
                "tag": "auxins",
                "input": "/aux/{num_auxin}/fdr",
                "input_padding": {"num_auxin": 1},
                "output": "/auxin/{num_auxin}/mix_fader",
                "data_index": 1,
                "write_transform": "fader_to_db",
                "secondary_output": {
                    "_db": {
                        "data_index": 0,
                    },
                },
            },
            {
                "tag": "auxins",
                "input": "/aux/{num_auxin}/mute",
                "input_padding": {"num_auxin": 1},
                "output": "/auxin/{num_auxin}/mix_on",
                "data_type": "boolean_inverted",
                "data_index": 2,
            },
            {
                "tag": "auxins",
                "input": "/aux/{num_auxin}/$name",
                "input_padding": {"num_auxin": 1},
                "output": "/auxin/{num_auxin}/config_name",
            },
            {
                "tag": "auxins",
                "input": "/aux/{num_auxin}/col",
                "input_padding": {"num_auxin": 1},
                "output": "/auxin/{num_auxin}/config_color",
                "data_index": 2,
                "secondary_output": {
                    "_name": {
                        "forward_function": "wing_color_index_to_name",
                        "reverse_function": "wing_color_name_to_index",
                    },
                },
            },
            # Busses
            {
                "tag": "busses",
                "input": "/bus/{num_bus}/fdr",
                "output": "/bus/{num_bus}/mix_fader",
                "input_padding": {"num_bus": 1},
                "data_index": 1,
                "write_transform": "fader_to_db",
                "secondary_output": {
                    "_db": {
                        "data_index": 0,
                    },
                },
            },
            {
                "tag": "busses",
                "input": "/bus/{num_bus}/mute",
                "output": "/bus/{num_bus}/mix_on",
                "input_padding": {"num_bus": 1},
                "data_type": "boolean_inverted",
                "data_index": 2,
            },
            {
                "tag": "busses",
                "input": "/bus/{num_bus}/$name",
                "output": "/bus/{num_bus}/config_name",
                "input_padding": {"num_bus": 1},
            },
            {
                "tag": "busses",
                "input": "/bus/{num_bus}/$col",
                "output": "/bus/{num_bus}/config_color",
                "input_padding": {"num_bus": 1},
                "data_index": 2,
                "secondary_output": {
                    "_name": {
                        "forward_function": "wing_color_index_to_name",
                        "reverse_function": "wing_color_name_to_index",
                    },
                },
            },
            # Bus Matrix Sends
            {
                "tag": "bussends",
                "input": "/bus/{num_bus}/send/MX{num_matrix}/on",
                "input_padding": {"num_matrix": 1, "num_bus": 1},
                "output": "/bussend/{num_bus}/{num_matrix}/mix_on",
                "data_type": "boolean",
                "data_index": 2,
            },
            {
                "tag": "bussends",
                "input": "/bus/{num_bus}/send/MX{num_matrix}/lvl",
                "input_padding": {"num_matrix": 1, "num_bus": 1},
                "output": "/bussend/{num_bus}/{num_matrix}/mix_fader",
                "write_transform": "fader_to_db",
                "data_index": 1,
                "secondary_output": {
                    "_db": {
                        "data_index": 0,
                    },
                },
            },
            {
                "tag": "bussends",
                "input": "/bus/{num_bus}/send/MX{num_matrix}/pre",
                "input_padding": {"num_matrix": 1, "num_bus": 1},
                "output": "/bussend/{num_bus}/{num_matrix}/pre",
                "data_type": "boolean",
                "data_index": 2,
            },
            # Bus -> Bus Sends (WING allows self-sends)
            {
                "tag": "busbussends",
                "input": "/bus/{num_bus}/send/{num_bus_send}/on",
                "input_padding": {"num_bus": 1, "num_bus_send": 1},
                "output": "/busbussend/{num_bus}/{num_bus_send}/mix_on",
                "data_type": "boolean",
                "data_index": 2,
            },
            {
                "tag": "busbussends",
                "input": "/bus/{num_bus}/send/{num_bus_send}/lvl",
                "input_padding": {"num_bus": 1, "num_bus_send": 1},
                "output": "/busbussend/{num_bus}/{num_bus_send}/mix_fader",
                "write_transform": "fader_to_db",
                "data_index": 1,
                "secondary_output": {
                    "_db": {
                        "data_index": 0,
                    },
                },
            },
            {
                "tag": "busbussends",
                "input": "/bus/{num_bus}/send/{num_bus_send}/pre",
                "input_padding": {"num_bus": 1, "num_bus_send": 1},
                "output": "/busbussend/{num_bus}/{num_bus_send}/pre",
                "data_type": "boolean",
                "data_index": 2,
            },
            # Bus Mains Sends
            {
                "tag": "busmainsends",
                "input": "/bus/{num_bus}/main/{num_mains}/on",
                "input_padding": {"num_mains": 1, "num_bus": 1},
                "output": "/busmainsend/{num_bus}/{num_mains}/mix_on",
                "data_type": "boolean",
                "data_index": 2,
            },
            {
                "tag": "busmainsends",
                "input": "/bus/{num_bus}/main/{num_mains}/lvl",
                "input_padding": {"num_mains": 1, "num_bus": 1},
                "output": "/busmainsend/{num_bus}/{num_mains}/mix_fader",
                "write_transform": "fader_to_db",
                "data_index": 1,
                "secondary_output": {
                    "_db": {
                        "data_index": 0,
                    },
                },
            },
            {
                "tag": "busmainsends",
                "input": "/bus/{num_bus}/main/{num_mains}/pre",
                "input_padding": {"num_mains": 1, "num_bus": 1},
                "output": "/busmainsend/{num_bus}/{num_mains}/pre",
                "data_type": "boolean",
                "data_index": 2,
            },
            # Matrices
            {
                "tag": "matrices",
                "input": "/mtx/{num_matrix}/fdr",
                "output": "/mtx/{num_matrix}/mix_fader",
                "write_transform": "fader_to_db",
                "input_padding": {"num_matrix": 1},
                "data_index": 1,
                "secondary_output": {
                    "_db": {
                        "data_index": 0,
                    },
                },
            },
            {
                "tag": "matrices",
                "input": "/mtx/{num_matrix}/mute",
                "output": "/mtx/{num_matrix}/mix_on",
                "input_padding": {"num_matrix": 1},
                "data_type": "boolean_inverted",
                "data_index": 2,
            },
            {
                "tag": "matrices",
                "input": "/mtx/{num_matrix}/$name",
                "output": "/mtx/{num_matrix}/config_name",
                "input_padding": {"num_matrix": 1},
            },
            {
                "tag": "matrices",
                "input": "/mtx/{num_matrix}/$col",
                "output": "/mtx/{num_matrix}/config_color",
                "input_padding": {"num_matrix": 1},
                "data_index": 2,
                "secondary_output": {
                    "_name": {
                        "forward_function": "wing_color_index_to_name",
                        "reverse_function": "wing_color_name_to_index",
                    },
                },
            },
            # DCAs
            {
                "tag": "dcas",
                "input": "/dca/{num_dca}/fdr",
                "output": "/dca/{num_dca}/mix_fader",
                "write_transform": "fader_to_db",
                "input_padding": {"num_dca": 1},
                "data_index": 1,
                "secondary_output": {
                    "_db": {
                        "data_index": 0,
                    },
                },
            },
            {
                "tag": "dcas",
                "input": "/dca/{num_dca}/mute",
                "output": "/dca/{num_dca}/mix_on",
                "data_index": 2,
                "data_type": "boolean_inverted",
                "input_padding": {"num_dca": 1},
            },
            {
                "tag": "dcas",
                "input": "/dca/{num_dca}/name",
                "output": "/dca/{num_dca}/config_name",
                "input_padding": {"num_dca": 1},
            },
            {
                "tag": "dcas",
                "input": "/dca/{num_dca}/col",
                "output": "/dca/{num_dca}/config_color",
                "input_padding": {"num_dca": 1},
                "data_index": 2,
                "secondary_output": {
                    "_name": {
                        "forward_function": "wing_color_index_to_name",
                        "reverse_function": "wing_color_name_to_index",
                    },
                },
            },
            # Mains
            {
                "tag": "mains",
                "input": "/main/{num_mains}/fdr",
                "output": "/main/{num_mains}/mix_fader",
                "write_transform": "fader_to_db",
                "input_padding": {"num_mains": 1},
                "data_index": 1,
                "secondary_output": {
                    "_db": {
                        "data_index": 0,
                    },
                },
            },
            {
                "tag": "mains",
                "input": "/main/{num_mains}/mute",
                "output": "/main/{num_mains}/mix_on",
                "input_padding": {"num_mains": 1},
                "data_index": 2,
                "data_type": "boolean_inverted",
            },
            {
                "tag": "mains",
                "input": "/main/{num_mains}/$name",
                "output": "/main/{num_mains}/config_name",
                "input_padding": {"num_mains": 1},
            },
            {
                "tag": "mains",
                "input": "/main/{num_mains}/$col",
                "output": "/main/{num_mains}/config_color",
                "input_padding": {"num_mains": 1},
                "data_index": 2,
                "secondary_output": {
                    "_name": {
                        "forward_function": "wing_color_index_to_name",
                        "reverse_function": "wing_color_name_to_index",
                    },
                },
            },
            # Show
            {
                "tag": "show",
                "input": "/$ctl/lib/$actshow",
                "output": "/show/name",
                "data_index": 0,
            },
            {
                "tag": "show",
                "input": "/$ctl/lib/$actidx",
                "output": "/scene/current",
                "data_index": 0,
            },
            {
                "tag": "show",
                "input": "/$ctl/lib/$active",
                "output": "/scene/name",
                "data_index": 0,
            },
            {
                "tag": "show",
                "input": "/$ctl/lib/$actionidx",
                "output": "/scene/next_scene",
                "data_index": 0,
            },
            # USB
            {
                "tag": "usb",
                "input": "/play/$actstate",
                "output": "/usb/state",
            },
            {
                "tag": "usb",
                "input": "/play/$actfile",
                "output": "/usb/file",
            },

            # USB Recorder
            {
                "tag": "usbrec",
                "input": "/rec/$actstate",
                "output": "/usb/rec/state",
                # WING may return enum indices or strings depending on firmware;
                # include identity entries to avoid mapping to None.
                "mapping": {
                    0: "STOP",
                    1: "REC",
                    2: "PAUSE",
                    3: "ERROR",
                    "STOP": "STOP",
                    "REC": "REC",
                    "PAUSE": "PAUSE",
                    "ERROR": "ERROR",
                },
            },
            {
                "tag": "usbrec",
                "input": "/rec/$actfile",
                "output": "/usb/rec/file",
            },
            {
                "tag": "usbrec",
                "input": "/rec/$action",
                "output": "/usb/rec/action",
                "mapping": {
                    0: "STOP",
                    1: "REC",
                    2: "PAUSE",
                    3: "NEWFILE",
                    "STOP": "STOP",
                    "REC": "REC",
                    "PAUSE": "PAUSE",
                    "NEWFILE": "NEWFILE",
                },
            },
            {
                "tag": "usbrec",
                "input": "/rec/path",
                "output": "/usb/rec/path",
            },
            {
                "tag": "usbrec",
                "input": "/rec/resolution",
                "output": "/usb/rec/resolution",
            },
            {
                "tag": "usbrec",
                "input": "/rec/channels",
                "output": "/usb/rec/channels",
            },
            {
                "tag": "usbrec",
                "input": "/rec/$time",
                "output": "/usb/rec/time",
            },
            # Mute Groups
            {
                "tag": "mutegroups",
                "input": "/mgrp/{num_mute_groups}/mute",
                "output": "/mutegroups/{num_mute_groups}/on",
                "data_type": "boolean",
                "data_index": 2,
            },
            # Headamps (local sources)
            {
                "tag": "headamps",
                "input": "/io/in/LCL/{num_head_amp}/g",
                "output": "/headamp/{num_head_amp}/gain",
                "input_padding": {
                    "num_head_amp": 1,
                },
                "write_transform": "wing_headamp_gain_db_to_float",
                "data_index": 2,
                "secondary_output": {
                    "_db": {
                        "forward_function": "float_to_db",
                        "reverse_function": "db_to_float",
                    },
                },
            },
            {
                "tag": "headamps",
                "input": "/io/in/LCL/{num_head_amp}/vph",
                "output": "/headamp/{num_head_amp}/phantom",
                "input_padding": {
                    "num_head_amp": 1,
                },
                "data_type": "boolean",
                "data_index": 2,
            },
            {
                "tag": "headamps",
                "input": "/io/in/LCL/{num_head_amp}/name",
                "output": "/headamp/{num_head_amp}/config_name",
                "input_padding": {
                    "num_head_amp": 1,
                },
            },
            {
                "tag": "headamps",
                "input": "/io/in/LCL/{num_head_amp}/col",
                "output": "/headamp/{num_head_amp}/config_color",
                "input_padding": {
                    "num_head_amp": 1,
                },
                "data_index": 2,
                "secondary_output": {
                    "_name": {
                        "forward_function": "wing_color_index_to_name",
                        "reverse_function": "wing_color_name_to_index",
                    },
                },
            },

            # Headamps (AES50 A/B/C sources)
            {
                "tag": "headamps",
                "input": "/io/in/A/{num_aes50_in}/g",
                "output": "/headamp/a/{num_aes50_in}/gain",
                "input_padding": {
                    "num_aes50_in": 1,
                },
                "write_transform": "wing_headamp_gain_db_to_float",
                "data_index": 2,
                "secondary_output": {
                    "_db": {
                        "forward_function": "float_to_db",
                        "reverse_function": "db_to_float",
                    },
                },
            },
            {
                "tag": "headamps",
                "input": "/io/in/A/{num_aes50_in}/vph",
                "output": "/headamp/a/{num_aes50_in}/phantom",
                "input_padding": {
                    "num_aes50_in": 1,
                },
                "data_type": "boolean",
                "data_index": 2,
            },
            {
                "tag": "headamps",
                "input": "/io/in/A/{num_aes50_in}/name",
                "output": "/headamp/a/{num_aes50_in}/config_name",
                "input_padding": {
                    "num_aes50_in": 1,
                },
            },
            {
                "tag": "headamps",
                "input": "/io/in/A/{num_aes50_in}/col",
                "output": "/headamp/a/{num_aes50_in}/config_color",
                "input_padding": {
                    "num_aes50_in": 1,
                },
                "data_index": 2,
                "secondary_output": {
                    "_name": {
                        "forward_function": "wing_color_index_to_name",
                        "reverse_function": "wing_color_name_to_index",
                    },
                },
            },
            {
                "tag": "headamps",
                "input": "/io/in/B/{num_aes50_in}/g",
                "output": "/headamp/b/{num_aes50_in}/gain",
                "input_padding": {
                    "num_aes50_in": 1,
                },
                "write_transform": "wing_headamp_gain_db_to_float",
                "data_index": 2,
                "secondary_output": {
                    "_db": {
                        "forward_function": "float_to_db",
                        "reverse_function": "db_to_float",
                    },
                },
            },
            {
                "tag": "headamps",
                "input": "/io/in/B/{num_aes50_in}/vph",
                "output": "/headamp/b/{num_aes50_in}/phantom",
                "input_padding": {
                    "num_aes50_in": 1,
                },
                "data_type": "boolean",
                "data_index": 2,
            },
            {
                "tag": "headamps",
                "input": "/io/in/B/{num_aes50_in}/name",
                "output": "/headamp/b/{num_aes50_in}/config_name",
                "input_padding": {
                    "num_aes50_in": 1,
                },
            },
            {
                "tag": "headamps",
                "input": "/io/in/B/{num_aes50_in}/col",
                "output": "/headamp/b/{num_aes50_in}/config_color",
                "input_padding": {
                    "num_aes50_in": 1,
                },
                "data_index": 2,
                "secondary_output": {
                    "_name": {
                        "forward_function": "wing_color_index_to_name",
                        "reverse_function": "wing_color_name_to_index",
                    },
                },
            },
            {
                "tag": "headamps",
                "input": "/io/in/C/{num_aes50_in}/g",
                "output": "/headamp/c/{num_aes50_in}/gain",
                "input_padding": {
                    "num_aes50_in": 1,
                },
                "write_transform": "wing_headamp_gain_db_to_float",
                "data_index": 2,
                "secondary_output": {
                    "_db": {
                        "forward_function": "float_to_db",
                        "reverse_function": "db_to_float",
                    },
                },
            },
            {
                "tag": "headamps",
                "input": "/io/in/C/{num_aes50_in}/vph",
                "output": "/headamp/c/{num_aes50_in}/phantom",
                "input_padding": {
                    "num_aes50_in": 1,
                },
                "data_type": "boolean",
                "data_index": 2,
            },
            {
                "tag": "headamps",
                "input": "/io/in/C/{num_aes50_in}/name",
                "output": "/headamp/c/{num_aes50_in}/config_name",
                "input_padding": {
                    "num_aes50_in": 1,
                },
            },
            {
                "tag": "headamps",
                "input": "/io/in/C/{num_aes50_in}/col",
                "output": "/headamp/c/{num_aes50_in}/config_color",
                "input_padding": {
                    "num_aes50_in": 1,
                },
                "data_index": 2,
                "secondary_output": {
                    "_name": {
                        "forward_function": "wing_color_index_to_name",
                        "reverse_function": "wing_color_name_to_index",
                    },
                },
            },
        ]

        super().__init__(**kwargs)
