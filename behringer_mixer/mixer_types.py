import importlib
from .MixerBase import MixerBase


class MixerTypeBase(MixerBase):
    # Base Mixer Type class
    mixer_type: str = ""
    port_number: int = 10023
    delay: float = 0.02
    num_channel: int = 0
    num_bus: int = 0
    num_dca: int = 0
    num_fx: int = 0
    num_auxrtn: int = 0
    num_matrix: int = 0
    num_scenes: int = 100

    addresses_to_load = [
        ["/ch/{num_channel}/mix/fader"],
        ["/ch/{num_channel}/mix/on"],
        ["/ch/{num_channel}/config/name"],
        ["/bus/{num_bus}/mix/fader"],
        ["/bus/{num_bus}/mix/on"],
        ["/bus/{num_bus}/config/name"],
        ["/mtx/{num_matrix:2}/mix/fader"],
        ["/mtx/{num_matrix:2}/mix/on"],
        ["/mtx/{num_matrix:2}/config/name"],
        ["/dca/{num_dca}/fader"],
        ["/dca/{num_dca}/on"],
        ["/dca/{num_dca}/config/name"],
        ["/main/st/mix/fader"],
        ["/main/st/mix/on"],
        ["/main/st/config/name"],
        ["/-show/showfile/show/name"],
        ["/-show/prepos/current", "/scene/current"],
    ]

    cmd_scene_load = "/-action/goscene"


class MixerTypeXAir(MixerTypeBase):
    # Base Mixer class for the XAir type mixers
    port_number: int = 10024

    cmd_scene_load = "/-snap/load"

    extra_addresses_to_load = [
        ["/main/lr/fader", "/main/st/mix/fader"],
        ["/main/lr/mix/on", "/main/st/mix/on"],
        ["/main/lr/config/name", "/main/st/config/name"],
    ]

    def __init__(*args):
        self.address_to_load.append(self.extra_address_to_load)
        super().__init__(*args)


class MixerTypeX32(MixerTypeBase):
    mixer_type: str = "X32"
    num_channel: int = 32
    num_bus: int = 16
    num_dca: int = 8
    num_fx: int = 8
    num_auxrtn: int = 8
    num_matrix: int = 6


class MixerTypeXR12(MixerTypeXAir):
    mixer_type: str = "XR12"
    num_channel: int = 12
    num_bus: int = 2
    num_dca: int = 4
    num_fx: int = 4


class MixerTypeXR16(MixerTypeXAir):
    mixer_type: str = "XR16"
    num_channel: int = 16
    num_bus: int = 4
    num_dca: int = 4
    num_fx: int = 4


class MixerTypeXR18(MixerTypeXAir):
    mixer_type: str = "XR18"
    num_channel: int = 16
    num_bus: int = 6
    num_dca: int = 4
    num_fx: int = 4
    num_auxrtn: int = 2


_supported_mixers = [
    "X32",
    "XR18",
    "XR16",
    "XR12",
]


def make_mixer(mixer_type, **kwargs):
    if mixer_type in _supported_mixers:
        mixer_class_name = "MixerType" + mixer_type
        module_ = importlib.import_module(".mixer_types", package="behringer_mixer")
        mixer_class = getattr(module_, mixer_class_name)
        c = mixer_class(**kwargs)
        return c
    return None