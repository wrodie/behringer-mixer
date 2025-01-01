import pytest
from behringer_mixer.utils import (
    fader_to_db,
    db_to_fader,
    color_name_to_index,
    color_index_to_name,
    linf_to_db,
    db_to_linf,
)


@pytest.mark.parametrize(
    "value, expected",
    [(100, 10), (0.75, 0), (1, 10), (0.37829911708831787, -19.7), (0, -90)],
)
def test_fader_to_db(value, expected):
    assert fader_to_db(value, {}) == expected


@pytest.mark.parametrize(
    "value, expected",
    [(100, 1), (0, 0.75), (10, 1), (-19.7, 0.37875000000000003), (-90, 0)],
)
def test_db_to_fader(value, expected):
    assert db_to_fader(value, {}) == expected


@pytest.mark.parametrize(
    "value, expected",
    [("OFF", 0), ("RD", 1), ("WHi", 15), ("OFFi", 8), ("BLi", 12)],
)
def test_color_name_to_index(value, expected):
    assert color_name_to_index(value, {}) == expected


@pytest.mark.parametrize(
    "expected, value",
    [("OFF", 0), ("RD", 1), ("WHi", 15), ("OFFi", 8), ("BLi", 12)],
)
def test_color_index_to_name(value, expected):
    assert color_index_to_name(value, {}) == expected


@pytest.mark.parametrize(
    "value, expected, min, max",
    [
        (1.0, 60, -12, 60),
        (0.8912509381337456, 52.17006754562968, -12, 60),
        (0.1, -4.8, -12, 60),
        (0.0, -12, -12, 60),
    ],
)
def test_linf_to_db(value, expected, min, max):
    config = {"data_type_config": {"min": min, "max": max}}
    assert linf_to_db(value, config) == expected


@pytest.mark.parametrize(
    "expected, value, min, max",
    [
        (1.0, 60, -12, 60),
        (0.8912509381337456, 52.17006754562968, -12, 60),
        (0.1, -4.8, -12, 60),
        (0.0, -12, -12, 60),
    ],
)
def test_db_to_linf(value, expected, min, max):
    config = {"data_type_config": {"min": min, "max": max}}
    assert db_to_linf(value, config) == expected
