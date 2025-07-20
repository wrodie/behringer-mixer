def fader_to_db(value, config):
    """Convert fader value to dB"""
    if value >= 1:
        return 10
    elif value >= 0.5:
        return round((40 * value) - 30, 1)
    elif value >= 0.25:
        return round((80 * value) - 50, 1)
    elif value >= 0.0625:
        return round((160 * value) - 70, 1)
    elif value >= 0:
        return round((480 * value) - 90, 1)
    else:
        return -90


def db_to_fader(value, config):
    """Convert dB to fader value"""
    if value >= 10:
        return 1
    elif value >= -10:
        return (value + 30) / 40
    elif value >= -30:
        return (value + 50) / 80
    elif value >= -60:
        return (value + 70) / 160
    elif value >= -90:
        return (value + 90) / 480
    return 0


_colors = [
    "OFF",
    "RD",
    "GN",
    "YE",
    "BL",
    "MG",
    "CY",
    "WH",
    "OFFi",
    "RDi",
    "GNi",
    "YEi",
    "BLi",
    "MGi",
    "CYi",
    "WHi",
]


def color_name_to_index(color_name: str, config) -> int:
    """Convert color name to color index"""
    return _colors.index(color_name)


def color_index_to_name(color_index: int, config) -> str:
    """Convert color index to color name"""
    return _colors[color_index]


def linf_to_db(value, config):
    """Convert linear fader value to dB"""
    max = 0
    min = 0
    if config and config.get("data_type_config"):
        min = config["data_type_config"].get("min")
        max = config["data_type_config"].get("max")
    return min + (max - min) * value


def db_to_linf(value, config):
    """Convert dB to linear fader value"""
    max = 0
    min = 0
    if config and config.get("data_type_config"):
        min = config["data_type_config"].get("min")
        max = config["data_type_config"].get("max")
    return (value - min) / (max - min)


_wing_colors = [
    "OFF",
    "GRAY_BLUE",
    "MEDIUM_BLUE",
    "DARK_BLUE",
    "TURQUOISE",
    "GREEN",
    "OLIVE_GREEN",
    "YELLOW",
    "ORANGE",
    "RED",
    "CORAL",
    "PINK",
    "MAUVE",
]


def wing_color_name_to_index(color_name: str, config) -> int:
    """Convert color name to color index"""
    return _wing_colors.index(color_name)


def wing_color_index_to_name(color_index: int, config) -> str:
    """Convert color index to color name"""
    return _wing_colors[int(color_index)]
