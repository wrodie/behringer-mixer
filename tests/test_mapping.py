import pytest
import json
from behringer_mixer import mixer_api

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_mixer_x32():
    # Open and read the JSON file
    with open("tests/x32mapping.json", "r") as file:
        json_data = json.load(file)
        mixer = mixer_api.create("X32", ip="192.168.1.1")
        mapping = json.dumps(mixer.dump_mapping())
        existing = json.dumps(json_data)
        assert mapping == existing


@pytest.mark.asyncio
async def test_mixer_xr16():
    # Open and read the JSON file
    with open("tests/xr16mapping.json", "r") as file:
        json_data = json.load(file)
        mixer = mixer_api.create("XR16", ip="192.168.1.1")
        mapping = json.dumps(mixer.dump_mapping())
        existing = json.dumps(json_data)
        print(mapping)
        assert mapping == existing
