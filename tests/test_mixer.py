import asyncio
import pytest
import yaml
import time
from behringer_mixer import mixer_api

pytest_plugins = ('pytest_asyncio',)

def load_test_mixer_config():
    config = yaml.safe_load(open("tests/test_mixer_config.yaml"))
    return config

@pytest.mark.asyncio
async def test_mixer():
    config = load_test_mixer_config()

    mixer = mixer_api.connect(config.get("mixer_type"), ip=config.get("ip"))
    start = time.process_time()
    await mixer.start()
    start = time.process_time()
    await mixer.reload()

    #Test channels
    start = time.process_time()
    await fader_sub_test(mixer, 'ch', mixer.num_channel)
    start = time.process_time()
    await fader_sub_test(mixer, 'bus', mixer.num_bus)
    start = time.process_time()
    await fader_sub_test(mixer, 'mtx', mixer.num_matrix)
    start = time.process_time()
    await fader_sub_test(mixer, 'dca', mixer.num_dca)

    start = time.process_time()
    await mixer.load_scene(6)
    start = time.process_time()
    assert mixer.state('/scene/current') == 6
    await mixer.stop()

async def fader_sub_test(mixer, prefix, num_faders):
    for fader_num in range(1, num_faders + 1):
        value = fader_num*3/100
        address = f"/{prefix}/{fader_num}/mix_fader"
        await mixer.set_value(address, value)
        expected_value = float(mixer.state(address) or 0)
        assert round(expected_value, 2) == value

        for value in (False, True):
            address = f"/{prefix}/{fader_num}/mix_on"
            await mixer.set_value(address, value)
            expected_value = mixer.state(address)
            assert expected_value == value
