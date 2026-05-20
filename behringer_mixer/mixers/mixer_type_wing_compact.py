from .mixer_type_wing import MixerTypeWING


class MixerTypeWINGCOMPACT(MixerTypeWING):
    """Class for Behringer WING Compact Mixer"""

    mixer_type: str = "WINGCOMPACT"
    num_head_amp: int = 24
