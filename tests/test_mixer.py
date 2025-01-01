import pytest
import yaml
from behringer_mixer import mixer_api

pytest_plugins = ("pytest_asyncio",)


def load_test_mixer_config():
    config = yaml.safe_load(open("tests/test_mixer_config.yaml"))
    return config


@pytest.mark.asyncio
async def test_mixer():
    config = load_test_mixer_config()

    mixer = mixer_api.create(config.get("mixer_type"), ip=config.get("ip"))
    await mixer.start()
    await mixer.reload()

    # Test channels
    await fader_sub_test(mixer, "ch", mixer.num_channel)
    await fader_sub_test(mixer, "bus", mixer.num_bus)
    await fader_sub_test(mixer, "mtx", mixer.num_matrix)
    await fader_sub_test(mixer, "dca", mixer.num_dca)
    await fader_sub_test(mixer, "auxin", mixer.num_auxin)

    await mixer.load_scene(1)
    assert mixer.state("/scene/current") == 1
    await mixer.stop()


async def fader_sub_test(mixer, prefix, num_faders):
    for fader_num in range(1, num_faders + 1):
        value = fader_num * 3 / 100
        address = f"/{prefix}/{fader_num}/mix_fader"
        await mixer.set_value(address, value)
        expected_value = float(mixer.state(address) or 0)
        assert round(expected_value, 2) == value

        for value in (False, True):
            address = f"/{prefix}/{fader_num}/mix_on"
            await mixer.set_value(address, value)
            expected_value = mixer.state(address)
            assert expected_value == value
