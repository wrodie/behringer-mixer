from .mixer_types import make_mixer


def connect(mixer_type: str, *args, **kwargs):
    """
    Interface entry point. Wraps factory expression and handles errors
    Returns a reference to a mixer
    """
    mixer_class = None
    try:
        mixer_class = make_mixer(mixer_type, **kwargs)
    except ValueError as e:
        raise SystemExit(e)
    return mixer_class
