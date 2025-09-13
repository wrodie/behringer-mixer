from .mixer_type_xair import MixerTypeXAir


class MixerTypeXR18(MixerTypeXAir):
    """Class for Behringer XR-18 Mixer"""

    mixer_type: str = "XR18"
    num_channel: int = 16
    num_bus: int = 6
    num_dca: int = 4
    num_fx: int = 4
    num_auxrtn: int = 2
    num_head_amp: int = 16
    num_mute_groups: int = 4
