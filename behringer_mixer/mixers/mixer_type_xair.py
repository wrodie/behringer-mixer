from .mixer_type_xseries_base import MixerTypeXSeriesBase


class MixerTypeXAir(MixerTypeXSeriesBase):
    """Base Mixer class for the XAir type mixers"""

    port_number: int = 10024
    cmd_scene_load = "/-snap/load"

    def __init__(self, **kwargs):
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
