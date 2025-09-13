from .mixer_type_xseries_base import MixerTypeXSeriesBase


class MixerTypeX32(MixerTypeXSeriesBase):
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
    num_mute_groups: int = 6
    num_head_amp: int = 128

    def __init__(self, **kwargs):
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
            # X USB Settings
            {
                "tag": "cards",
                "input": "/-prefs/card/USBmode",
                "output": "/config/cards/XUSBmode",
                "mapping": {
                    0: "32in/32out",
                    1: "16in/16out",
                    2: "32in/8out",
                    3: "8in/32out",
                    4: "8in/8out",
                    5: "2in/2out",
                },
            },
        ]
        super().__init__(**kwargs)
