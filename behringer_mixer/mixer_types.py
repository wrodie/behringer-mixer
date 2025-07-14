from .mixers.mixer_type_x32 import MixerTypeX32
from .mixers.mixer_type_xr18 import MixerTypeXR18
from .mixers.mixer_type_xr16 import MixerTypeXR16
from .mixers.mixer_type_xr12 import MixerTypeXR12
from .mixers.mixer_type_wing import MixerTypeWING

_supported_mixers = [
    "X32",
    "XR18",
    "XR16",
    "XR12",
    "WING",
]


def make_mixer(mixer_type, **kwargs):
    """Make the actual mixer object based on the type"""
    if mixer_type in _supported_mixers:
        mixer_class_name = "MixerType" + mixer_type
        mixer_class_map = {
            "MixerTypeX32": MixerTypeX32,
            "MixerTypeXR18": MixerTypeXR18,
            "MixerTypeXR16": MixerTypeXR16,
            "MixerTypeXR12": MixerTypeXR12,
            "MixerTypeWING": MixerTypeWING,
        }
        mixer_class = mixer_class_map.get(mixer_class_name)
        if mixer_class:
            return mixer_class(**kwargs)
    return None
