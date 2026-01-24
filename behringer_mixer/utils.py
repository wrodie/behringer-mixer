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
    # WING firmware >= 3.1 exposes 18 colors.
    # OSC returns (string, normalized, int) where the string value is 1-based.
    # 0-based list of the 18 color names, convert at the boundary.
    "GRAY_BLUE",
    "MEDIUM_BLUE",
    "DARK_BLUE",
    "TURQUOISE",
    "GREEN",
    "OLIVE_GREEN",
    "YELLOW",
    "BROWN",
    "RED",
    "CORAL",
    "MAGENTA",
    "PURPLE",
    "ORANGE",
    "LIGHT_BLUE",
    "SALMON",
    "TEAL",
    "DARK_GRAY",
    "LIGHT_GRAY",
]


def wing_color_name_to_index(color_name: str, config) -> int:
    """Convert color name to color index"""
    if color_name in _wing_colors:
        return _wing_colors.index(color_name) + 1
    # Allow round-tripping unknown indices exposed as strings (e.g. "COLOR_14").
    if isinstance(color_name, str) and color_name.startswith("COLOR_"):
        suffix = color_name.removeprefix("COLOR_")
        try:
            # Treat this as an external 1-based index.
            return int(suffix)
        except ValueError as err:
            raise ValueError(f"Invalid WING color name: {color_name}") from err
    raise ValueError(f"Unknown WING color name: {color_name}")


def wing_color_index_to_name(color_index: int, config) -> str:
    """Convert color index to color name"""
    try:
        idx = int(float(color_index))
    except (TypeError, ValueError):
        return "UNKNOWN"

    # External is 1-based; convert to internal 0-based.
    idx0 = idx - 1
    if 0 <= idx0 < len(_wing_colors):
        return _wing_colors[idx0]

    return f"COLOR_{idx}"


def float_to_db(value, config):
    """Pass-through conversion for values that are already in dB."""
    return value


def db_to_float(value, config):
    """Inverse of float_to_db (pass-through)."""
    return value


def wing_headamp_gain_db_to_float(value, config):
    """Normalize WING headamp gain values.

    Field tests show local headamp gain uses 2.5 dB steps and a range
    of -2.5 .. 45.0 dB on current firmware (docs claim 0.5 dB).
    """
    try:
        gain_db = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid headamp gain value: {value!r}")

    gain_db = max(-2.5, min(45.0, gain_db))
    gain_db = round(gain_db / 2.5) * 2.5
    gain_db = max(-2.5, min(45.0, gain_db))
    return gain_db
