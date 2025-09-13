from ..mixer_base import MixerBase


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
    num_mute_groups: int = 0
    has_mono: bool = False
    num_mains: int = 1
    info_address: str = "/xinfo"
    subscription_string: str = "/xremote"
    subscription_renew_string: str = "/renew"

    addresses_to_load = []

    cmd_scene_load = "/-action/goscene"
    cmd_scene_execute = None

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
            "bus_mainsends": {
                "number": 0,
                "base_address": "busmainsend",
            },
            "head_amps": {
                "number": self.num_head_amp,
                "base_address": "headamp",
            },
            "mains": {
                "number": self.num_mains,
                "base_address": "main",
            },
            "mute_groups": {
                "number": self.num_mute_groups,
                "base_address": "mutegroups",
            },
            "has_mono": self.has_mono,
        }
