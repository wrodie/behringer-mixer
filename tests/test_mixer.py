import pytest
import yaml
import time
from behringer_mixer import mixer_api

def load_test_mixer_config():
    config = yaml.safe_load(open("tests/test_mixer_config.yaml"))
    return config

def test_mixer():
    config = load_test_mixer_config()

    with mixer_api.connect(config.get("mixer_type"), ip=config.get("ip")) as mixer:
        #Test channels
        fader_sub_test(mixer, 'ch', mixer.num_channel)
        fader_sub_test(mixer, 'bus', mixer.num_bus)
        fader_sub_test(mixer, 'mtx', mixer.num_matrix)
        dca_sub_test(mixer, 'dca', mixer.num_dca)

        mixer.load_scene(6)
        mixer.reload()
        assert mixer.state('/scene/current') == 6

def fader_sub_test(mixer, prefix, num_faders):
    for fader_num in range(1, num_faders + 1):
        value = fader_num*3/100
        address = f"/{prefix}/{fader_num}/mix_fader"
        mixer.set_value(address, value)
        expected_value = float(mixer.state(address))
        assert round(expected_value, 2) == value

        for value in (False, True):
            address = f"/{prefix}/{fader_num}/mix_on"
            mixer.set_value(address, value)
            expected_value = mixer.state(address)
            assert expected_value == value

def dca_sub_test(mixer, prefix, num_faders):
    for fader_num in range(1, num_faders + 1):
        value = fader_num*3/100
        address = f"/{prefix}/{fader_num}/fader"
        mixer.set_value(address, value)
        expected_value = float(mixer.state(address))
        assert round(expected_value, 2) == value

        for value in (False, True):
            address = f"/{prefix}/{fader_num}/on"
            mixer.set_value(address, value)
            expected_value = mixer.state(address)
            assert expected_value == value
