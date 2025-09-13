from .mixer_type_xair import MixerTypeXAir


class MixerTypeXR12(MixerTypeXAir):
    """Class for Behringer XR-12 Mixer"""

    mixer_type: str = "XR12"
    num_channel: int = 12
    num_bus: int = 2
    num_dca: int = 4
    num_fx: int = 4
    num_head_amp: int = 4
    num_mute_groups: int = 4
