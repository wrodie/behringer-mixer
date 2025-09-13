from .mixer_type_xair import MixerTypeXAir


class MixerTypeXR16(MixerTypeXAir):
    """Class for Behringer XR-16 Mixer"""

    mixer_type: str = "XR16"
    num_channel: int = 16
    num_bus: int = 4
    num_dca: int = 4
    num_fx: int = 4
    num_head_amp: int = 8
    num_mute_groups: int = 4
