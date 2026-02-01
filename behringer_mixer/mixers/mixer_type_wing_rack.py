from .mixer_type_wing import MixerTypeWING


class MixerTypeWINGRACK(MixerTypeWING):
    """Class for Behringer WING Rack Mixer"""

    mixer_type: str = "WINGRACK"
    num_head_amp: int = 24
