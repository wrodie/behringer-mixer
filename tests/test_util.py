import pytest
from behringer_mixer.utils import fader_to_db, db_to_fader


@pytest.mark.parametrize("value, expected", [(100, 10), (0.75, 0), (1, 10), (0.37829911708831787,-19.7), (0, -90)])
def test_fader_to_db(value, expected):
    assert fader_to_db(value) == expected

@pytest.mark.parametrize("value, expected", [(100, 1), (0, 0.75), (10, 1), (-19.7, 0.37875000000000003), (-90,0)])
def test_db_to_fader(value, expected):
    assert db_to_fader(value) == expected
