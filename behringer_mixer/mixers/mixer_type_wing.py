"""Behringer WING OSC mapping notes (field findings + protocol quirks)

The notes below are based on:
- The Behringer WING remote protocol documentation (the PDF is partially outdated on a few points).
- Multiple live tests against a real console fimware 3.1.

1) `/name` vs `/$name` (and `.../name` writeability)
    - Use `/.../name` for both reads and writes.
    - The `/$name` endpoints may respond to reads, but they are not reliably writable
      (they behave like "read-only / linked" reflection).
    - Our mapping outputs use `/.../config_name` (library-level key), with input set to `/.../name`.
    - Practical length limits (observed):
        - Most strips: 16 chars
        - DCA: 8 chars

2) `/col` vs `/$col` (and `/col` reply payload format)
    - Use `/.../col` for both reads and writes.
    - The `/$col` endpoints behave like the `/$name` ones: reads may work, writes are unreliable.
    - Important: WING’s reply to `/.../col` is *multi-value*. Example payload observed:
         ('9', 0.47058823529411764, 8)
      Interpreted as:
        - element[0]: 1-based color index as a STRING ("1".."18")
        - element[1]: normalized float (approximately (idx-1)/17)
        - element[2]: 0-based index as int (idx-1)
    - For stable round-tripping we store the external 1-based index from element[0]
      (`data_type: int`, `data_index: 0`).
    - The OSC stack sometimes delivers numeric values as strings!

3) Color count: documentation says 12, firmware >= 3.1 exposes 18
    - We treat indices as:
        - 1..18 for named colors
        - 0 as OFF/none (seen on some objects)
    - Name<->index helpers (`wing_color_*`) are implemented for 18 colors. Unknown values
      round-trip as "COLOR_<n>".

4) Color writeability can be object-dependent
    - On the tested console, channel/aux/bus/main/matrix colors were writable.
    - DCA and some headamp color endpoints appeared to ignore writes.

5) Headamps: local (LCL) and AES50 (A/B/C)
    - Local headamps are addressed via `/io/in/LCL/<n>/...`.
    - AES50 headamps are addressed via `/io/in/A|B|C/<n>/...`.
    - We expose them as library keys:
        - gain:    `/headamp/<n>/gain` (LCL) and `/headamp/a|b|c/<n>/gain` (AES)
        - phantom: `/headamp/<n>/phantom` and `/headamp/a|b|c/<n>/phantom`
        - name:    `/headamp/.../config_name`
        - color:   `/headamp/.../config_color`
    - Phantom (`.../vph`) was writable and read back reliably.
    - Gain writes work when Remote Lock is OFF and no competing OSC client is connected.
    - LCL gain step size is 2.5 dB (matches UI), not 0.5 dB as docs suggest. Occasional read
      timeouts on individual steps were observed.
    - Both `/io/in/LCL/<n>/g` (source) and `/ch/<n>/in/set/$g` (channel) write paths work.
        - Use tag `headamps` for source-type (LCL/A/B/C) access.
    - Stereo input pairs explain "missing" even LCL patches (e.g. 5/6, 7/8, 9/10...).
    - AES50 inputs return default values even with no stagebox connected; occasional empty fields
      are expected (timing/response drop).

6) Channel preamp settings (/ch/<n>/in/set/* and /ch/<n>/in/conn/*)
    - Mapped and read-tested:
        - Input mode: `/ch/<n>/in/set/$mode` (M/ST/M-S)
        - Source switches: `/ch/<n>/in/set/srcauto`, `/ch/<n>/in/set/altsrc`
        - Polarity: `/ch/<n>/in/set/inv`
        - Trim/Balance: `/ch/<n>/in/set/trim`, `/ch/<n>/in/set/bal`
        - Preamp gain + phantom: `/ch/<n>/in/set/$g`, `/ch/<n>/in/set/$vph`
        - Input delay: `/ch/<n>/in/set/dlymode`, `/ch/<n>/in/set/dly`, `/ch/<n>/in/set/dlyon`
        - Connection: `/ch/<n>/in/conn/grp`, `/ch/<n>/in/conn/in`, `/ch/<n>/in/conn/altgrp`, `/ch/<n>/in/conn/altin`
    - Write-tested: inv, srcauto, altsrc, trim, bal,
        dlyon, dly, $vph. (Mode changes were not tested yet.)
    - Use tag `channelpreamp` for channel-based access.

7) Sends and “self-sends”
    - Bus → bus sends are mapped under tag `busbussends`.
    - Bus → bus sends where the source bus equals the destination bus are ignored by the console.
    - Bus → Matrix `pre` and Bus → Main `pre` are mapped (`/bus/<n>/send/MX<m>/pre`, `/bus/<n>/main/<m>/pre`).

8) `/status` is synthetic
    - We query `/ ?` for mixer info, but store it under the synthetic output `/status`.
    - WING may answer `/ ?` as `/ ?` or `/*`. `/*` is also used for generic ACK/ERROR strings.
        We only parse `/*` replies that start with `WING,`.
    - `/status` is not a real writable OSC endpoint.

9) USB player playlist behavior
    - `/play/$songs` returns the *first* song on a simple read. Use a node-level request
            (e.g. `/play/$songs` with value `?`) to retrieve the full playlist.
    - `/play/$actlist` points to the playlist file (e.g. `U:/SOUNDS/.plist`), not the folder.
    - Player actions (PLAY/PAUSE/STOP) return `ERROR` if no playlist/file is active.
    - To play reliably: open a playlist on the console, set `/play/$actidx` and send `PLAY`.

10) USB recorder behavior
    - Check `/usb/rec/state` and `/usb/rec/file`.
    - Trigger actions via `/usb/rec/action` (values: NEWFILE, REC, STOP, PAUSE).
    - Recorder actions: `NEWFILE` → `REC` → `STOP` worked and created a new file.
    - `/usb/rec/path` was removed.

11) WING variants
    - WINGRACK and WINGCOMPACT use the same mapping with a larger local headamp count (24).
"""

from .mixer_type_base import MixerTypeBase


class MixerTypeWING(MixerTypeBase):
    """Class for Behringer WING Mixer"""

    port_number: int = 2223
    mixer_type: str = "WING"
    num_channel: int = 40
    num_bus: int = 16
    num_bus_send: int = 16
    num_dca: int = 16
    num_fx: int = 0
    num_auxin: int = 8
    num_auxrtn: int = 0
    num_matrix: int = 8
    has_mono: bool = False
    num_head_amp: int = 8
    num_aes50_in: int = 48
    num_mains: int = 4
    num_mute_groups: int = 8
    info_address: str = "/?"
    subscription_string: str = "/*s"
    subscription_renew_string: str = "/*s"

    cmd_scene_load = "/$ctl/lib/$actionidx"
    cmd_scene_execute = ["/$ctl/lib/$action", "GO"]

    def __init__(self, **kwargs):
        self.extra_addresses_to_load = [
            # Mixer info (WING answers "/?" with a "/*" or "/?" response)
            {
                "input": "/?",
                "output": "/status",
            },
            # Channels
            {
                "tag": "channels",
                "input": "/ch/{num_channel}/fdr",
                "output": "/ch/{num_channel}/mix_fader",
                "input_padding": {
                    "num_channel": 1,
                },
                "data_index": 1,
                "write_transform": "fader_to_db",
                "secondary_output": {
                    "_db": {
                        "data_index": 0,
                    },
                },
            },
            {
                "tag": "channels",
                "input": "/ch/{num_channel}/mute",
                "output": "/ch/{num_channel}/mix_on",
                "input_padding": {
                    "num_channel": 1,
                },
                "data_type": "boolean_inverted",
                "data_index": 2,
            },
            {
                "tag": "channels",
                "input_padding": {
                    "num_channel": 1,
                },
                "input": "/ch/{num_channel}/name",
                "output": "/ch/{num_channel}/config_name",
            },
            {
                "tag": "channels",
                "input": "/ch/{num_channel}/col",
                "output": "/ch/{num_channel}/config_color",
                "input_padding": {
                    "num_channel": 1,
                },
                "data_type": "int",
                "data_index": 0,
                "secondary_output": {
                    "_name": {
                        "forward_function": "wing_color_index_to_name",
                        "reverse_function": "wing_color_name_to_index",
                    },
                },
            },
            {
                "tag": "channelpreamp",
                "input": "/ch/{num_channel}/in/set/$g",
                "output": "/ch/{num_channel}/preamp_gain",
                "input_padding": {
                    "num_channel": 1,
                },
                "data_index": 0,
                "write_transform": "wing_headamp_gain_db_to_float",
            },
            {
                "tag": "channelpreamp",
                "input": "/ch/{num_channel}/in/set/$vph",
                "output": "/ch/{num_channel}/preamp_phantom",
                "input_padding": {
                    "num_channel": 1,
                },
                "data_index": 0,
                "data_type": "boolean",
            },
            {
                "tag": "channelpreamp",
                "input": "/ch/{num_channel}/in/set/$mode",
                "output": "/ch/{num_channel}/input_mode",
                "input_padding": {
                    "num_channel": 1,
                },
                "data_index": 0,
            },
            {
                "tag": "channelpreamp",
                "input": "/ch/{num_channel}/in/set/srcauto",
                "output": "/ch/{num_channel}/input_srcauto",
                "input_padding": {
                    "num_channel": 1,
                },
                "data_index": 0,
                "data_type": "boolean",
            },
            {
                "tag": "channelpreamp",
                "input": "/ch/{num_channel}/in/set/altsrc",
                "output": "/ch/{num_channel}/input_altsrc",
                "input_padding": {
                    "num_channel": 1,
                },
                "data_index": 0,
                "data_type": "boolean",
            },
            {
                "tag": "channelpreamp",
                "input": "/ch/{num_channel}/in/set/inv",
                "output": "/ch/{num_channel}/input_invert",
                "input_padding": {
                    "num_channel": 1,
                },
                "data_index": 0,
                "data_type": "boolean",
            },
            {
                "tag": "channelpreamp",
                "input": "/ch/{num_channel}/in/set/trim",
                "output": "/ch/{num_channel}/input_trim",
                "input_padding": {
                    "num_channel": 1,
                },
                "data_index": 0,
            },
            {
                "tag": "channelpreamp",
                "input": "/ch/{num_channel}/in/set/bal",
                "output": "/ch/{num_channel}/input_balance",
                "input_padding": {
                    "num_channel": 1,
                },
                "data_index": 0,
            },
            {
                "tag": "channelpreamp",
                "input": "/ch/{num_channel}/in/set/dlymode",
                "output": "/ch/{num_channel}/input_delay_mode",
                "input_padding": {
                    "num_channel": 1,
                },
                "data_index": 0,
            },
            {
                "tag": "channelpreamp",
                "input": "/ch/{num_channel}/in/set/dly",
                "output": "/ch/{num_channel}/input_delay",
                "input_padding": {
                    "num_channel": 1,
                },
                "data_index": 0,
            },
            {
                "tag": "channelpreamp",
                "input": "/ch/{num_channel}/in/set/dlyon",
                "output": "/ch/{num_channel}/input_delay_on",
                "input_padding": {
                    "num_channel": 1,
                },
                "data_index": 0,
                "data_type": "boolean",
            },
            {
                "tag": "channelpreamp",
                "input": "/ch/{num_channel}/in/conn/grp",
                "output": "/ch/{num_channel}/input_conn_grp",
                "input_padding": {
                    "num_channel": 1,
                },
                "data_index": 0,
            },
            {
                "tag": "channelpreamp",
                "input": "/ch/{num_channel}/in/conn/in",
                "output": "/ch/{num_channel}/input_conn_in",
                "input_padding": {
                    "num_channel": 1,
                },
                "data_index": 0,
            },
            {
                "tag": "channelpreamp",
                "input": "/ch/{num_channel}/in/conn/altgrp",
                "output": "/ch/{num_channel}/input_alt_conn_grp",
                "input_padding": {
                    "num_channel": 1,
                },
                "data_index": 0,
            },
            {
                "tag": "channelpreamp",
                "input": "/ch/{num_channel}/in/conn/altin",
                "output": "/ch/{num_channel}/input_alt_conn_in",
                "input_padding": {
                    "num_channel": 1,
                },
                "data_index": 0,
            },
            # Channel Sends
            {
                "tag": "channelsends",
                "input": "/ch/{num_channel}/send/{num_bus}/on",
                "data_index": 2,
                "input_padding": {
                    "num_bus": 1,
                    "num_channel": 1,
                },
                "output": "/chsend/{num_channel}/{num_bus}/mix_on",
                "data_type": "boolean",
            },
            {
                "tag": "channelsends",
                "input": "/ch/{num_channel}/send/{num_bus}/lvl",
                "input_padding": {
                    "num_bus": 1,
                    "num_channel": 1,
                },
                "output": "/chsend/{num_channel}/{num_bus}/mix_fader",
                "data_index": 1,
                "secondary_output": {
                    "_db": {
                        "data_index": 0,
                    },
                },
            },
            # Auxins
            {
                "tag": "auxins",
                "input": "/aux/{num_auxin}/fdr",
                "input_padding": {"num_auxin": 1},
                "output": "/auxin/{num_auxin}/mix_fader",
                "data_index": 1,
                "write_transform": "fader_to_db",
                "secondary_output": {
                    "_db": {
                        "data_index": 0,
                    },
                },
            },
            {
                "tag": "auxins",
                "input": "/aux/{num_auxin}/mute",
                "input_padding": {"num_auxin": 1},
                "output": "/auxin/{num_auxin}/mix_on",
                "data_type": "boolean_inverted",
                "data_index": 2,
            },
            {
                "tag": "auxins",
                "input": "/aux/{num_auxin}/name",
                "input_padding": {"num_auxin": 1},
                "output": "/auxin/{num_auxin}/config_name",
            },
            {
                "tag": "auxins",
                "input": "/aux/{num_auxin}/col",
                "input_padding": {"num_auxin": 1},
                "output": "/auxin/{num_auxin}/config_color",
                "data_type": "int",
                "data_index": 0,
                "secondary_output": {
                    "_name": {
                        "forward_function": "wing_color_index_to_name",
                        "reverse_function": "wing_color_name_to_index",
                    },
                },
            },
            # Busses
            {
                "tag": "busses",
                "input": "/bus/{num_bus}/fdr",
                "output": "/bus/{num_bus}/mix_fader",
                "input_padding": {"num_bus": 1},
                "data_index": 1,
                "write_transform": "fader_to_db",
                "secondary_output": {
                    "_db": {
                        "data_index": 0,
                    },
                },
            },
            {
                "tag": "busses",
                "input": "/bus/{num_bus}/mute",
                "output": "/bus/{num_bus}/mix_on",
                "input_padding": {"num_bus": 1},
                "data_type": "boolean_inverted",
                "data_index": 2,
            },
            {
                "tag": "busses",
                "input": "/bus/{num_bus}/name",
                "output": "/bus/{num_bus}/config_name",
                "input_padding": {"num_bus": 1},
            },
            {
                "tag": "busses",
                "input": "/bus/{num_bus}/col",
                "output": "/bus/{num_bus}/config_color",
                "input_padding": {"num_bus": 1},
                "data_type": "int",
                "data_index": 0,
                "secondary_output": {
                    "_name": {
                        "forward_function": "wing_color_index_to_name",
                        "reverse_function": "wing_color_name_to_index",
                    },
                },
            },
            # Bus Matrix Sends
            {
                "tag": "bussends",
                "input": "/bus/{num_bus}/send/MX{num_matrix}/on",
                "input_padding": {"num_matrix": 1, "num_bus": 1},
                "output": "/bussend/{num_bus}/{num_matrix}/mix_on",
                "data_type": "boolean",
                "data_index": 2,
            },
            {
                "tag": "bussends",
                "input": "/bus/{num_bus}/send/MX{num_matrix}/lvl",
                "input_padding": {"num_matrix": 1, "num_bus": 1},
                "output": "/bussend/{num_bus}/{num_matrix}/mix_fader",
                "write_transform": "fader_to_db",
                "data_index": 1,
                "secondary_output": {
                    "_db": {
                        "data_index": 0,
                    },
                },
            },
            {
                "tag": "bussends",
                "input": "/bus/{num_bus}/send/MX{num_matrix}/pre",
                "input_padding": {"num_matrix": 1, "num_bus": 1},
                "output": "/bussend/{num_bus}/{num_matrix}/pre",
                "data_type": "boolean",
                "data_index": 2,
            },
            # Bus Mains Sends
            {
                "tag": "busmainsends",
                "input": "/bus/{num_bus}/main/{num_mains}/on",
                "input_padding": {"num_mains": 1, "num_bus": 1},
                "output": "/busmainsend/{num_bus}/{num_mains}/mix_on",
                "data_type": "boolean",
                "data_index": 2,
            },
            {
                "tag": "busmainsends",
                "input": "/bus/{num_bus}/main/{num_mains}/lvl",
                "input_padding": {"num_mains": 1, "num_bus": 1},
                "output": "/busmainsend/{num_bus}/{num_mains}/mix_fader",
                "write_transform": "fader_to_db",
                "data_index": 1,
                "secondary_output": {
                    "_db": {
                        "data_index": 0,
                    },
                },
            },
            {
                "tag": "busmainsends",
                "input": "/bus/{num_bus}/main/{num_mains}/pre",
                "input_padding": {"num_mains": 1, "num_bus": 1},
                "output": "/busmainsend/{num_bus}/{num_mains}/pre",
                "data_type": "boolean",
                "data_index": 2,
            },
            # Matrices
            {
                "tag": "matrices",
                "input": "/mtx/{num_matrix}/fdr",
                "output": "/mtx/{num_matrix}/mix_fader",
                "write_transform": "fader_to_db",
                "input_padding": {"num_matrix": 1},
                "data_index": 1,
                "secondary_output": {
                    "_db": {
                        "data_index": 0,
                    },
                },
            },
            {
                "tag": "matrices",
                "input": "/mtx/{num_matrix}/mute",
                "output": "/mtx/{num_matrix}/mix_on",
                "input_padding": {"num_matrix": 1},
                "data_type": "boolean_inverted",
                "data_index": 2,
            },
            {
                "tag": "matrices",
                "input": "/mtx/{num_matrix}/name",
                "output": "/mtx/{num_matrix}/config_name",
                "input_padding": {"num_matrix": 1},
            },
            {
                "tag": "matrices",
                "input": "/mtx/{num_matrix}/col",
                "output": "/mtx/{num_matrix}/config_color",
                "input_padding": {"num_matrix": 1},
                "data_type": "int",
                "data_index": 0,
                "secondary_output": {
                    "_name": {
                        "forward_function": "wing_color_index_to_name",
                        "reverse_function": "wing_color_name_to_index",
                    },
                },
            },
            # DCAs
            {
                "tag": "dcas",
                "input": "/dca/{num_dca}/fdr",
                "output": "/dca/{num_dca}/mix_fader",
                "write_transform": "fader_to_db",
                "input_padding": {"num_dca": 1},
                "data_index": 1,
                "secondary_output": {
                    "_db": {
                        "data_index": 0,
                    },
                },
            },
            {
                "tag": "dcas",
                "input": "/dca/{num_dca}/mute",
                "output": "/dca/{num_dca}/mix_on",
                "data_index": 2,
                "data_type": "boolean_inverted",
                "input_padding": {"num_dca": 1},
            },
            {
                "tag": "dcas",
                "input": "/dca/{num_dca}/name",
                "output": "/dca/{num_dca}/config_name",
                "input_padding": {"num_dca": 1},
            },
            {
                "tag": "dcas",
                "input": "/dca/{num_dca}/col",
                "output": "/dca/{num_dca}/config_color",
                "input_padding": {"num_dca": 1},
                "data_type": "int",
                "data_index": 0,
                "secondary_output": {
                    "_name": {
                        "forward_function": "wing_color_index_to_name",
                        "reverse_function": "wing_color_name_to_index",
                    },
                },
            },
            # Mains
            {
                "tag": "mains",
                "input": "/main/{num_mains}/fdr",
                "output": "/main/{num_mains}/mix_fader",
                "write_transform": "fader_to_db",
                "input_padding": {"num_mains": 1},
                "data_index": 1,
                "secondary_output": {
                    "_db": {
                        "data_index": 0,
                    },
                },
            },
            {
                "tag": "mains",
                "input": "/main/{num_mains}/mute",
                "output": "/main/{num_mains}/mix_on",
                "input_padding": {"num_mains": 1},
                "data_index": 2,
                "data_type": "boolean_inverted",
            },
            {
                "tag": "mains",
                "input": "/main/{num_mains}/name",
                "output": "/main/{num_mains}/config_name",
                "input_padding": {"num_mains": 1},
            },
            {
                "tag": "mains",
                "input": "/main/{num_mains}/col",
                "output": "/main/{num_mains}/config_color",
                "input_padding": {"num_mains": 1},
                "data_type": "int",
                "data_index": 0,
                "secondary_output": {
                    "_name": {
                        "forward_function": "wing_color_index_to_name",
                        "reverse_function": "wing_color_name_to_index",
                    },
                },
            },
            # Show
            {
                "tag": "show",
                "input": "/$ctl/lib/$actshow",
                "output": "/show/name",
                "data_index": 0,
            },
            {
                "tag": "show",
                "input": "/$ctl/lib/$actidx",
                "output": "/scene/current",
                "data_index": 0,
            },
            {
                "tag": "show",
                "input": "/$ctl/lib/$active",
                "output": "/scene/name",
                "data_index": 0,
            },
            {
                "tag": "show",
                "input": "/$ctl/lib/$actionidx",
                "output": "/scene/next_scene",
                "data_index": 0,
            },
            # USB
            {
                "tag": "usb",
                "input": "/play/$actstate",
                "output": "/usb/state",
            },
            {
                "tag": "usb",
                "input": "/play/$actfile",
                "output": "/usb/file",
            },
            {
                "tag": "usb",
                "input": "/play/$actlist",
                "output": "/usb/playlist/path",
            },
            {
                "tag": "usb",
                "input": "/play/$actidx",
                "output": "/usb/playlist/index",
                "data_index": 0,
            },
            {
                "tag": "usb",
                "input": "/play/$songs",
                "output": "/usb/playlist/songs",
            },

            # USB Recorder
            {
                "tag": "usbrec",
                "input": "/rec/$actstate",
                "output": "/usb/rec/state",
                # WING may return enum indices or strings depending on firmware;
                # include identity entries to avoid mapping to None.
                "mapping": {
                    0: "STOP",
                    1: "REC",
                    2: "PAUSE",
                    3: "ERROR",
                    "STOP": "STOP",
                    "REC": "REC",
                    "PAUSE": "PAUSE",
                    "ERROR": "ERROR",
                },
            },
            {
                "tag": "usbrec",
                "input": "/rec/$actfile",
                "output": "/usb/rec/file",
            },
            {
                "tag": "usbrec",
                "input": "/rec/$action",
                "output": "/usb/rec/action",
                "mapping": {
                    0: "STOP",
                    1: "REC",
                    2: "PAUSE",
                    3: "NEWFILE",
                    "STOP": "STOP",
                    "REC": "REC",
                    "PAUSE": "PAUSE",
                    "NEWFILE": "NEWFILE",
                },
            },
            {
                "tag": "usbrec",
                "input": "/rec/resolution",
                "output": "/usb/rec/resolution",
            },
            {
                "tag": "usbrec",
                "input": "/rec/channels",
                "output": "/usb/rec/channels",
            },
            {
                "tag": "usbrec",
                "input": "/rec/$time",
                "output": "/usb/rec/time",
            },
            # Mute Groups
            {
                "tag": "mutegroups",
                "input": "/mgrp/{num_mute_groups}/mute",
                "output": "/mutegroups/{num_mute_groups}/on",
                "data_type": "boolean",
                "data_index": 2,
            },
            # Headamps (local sources)
            {
                "tag": "headamps",
                "input": "/io/in/LCL/{num_head_amp}/g",
                "output": "/headamp/{num_head_amp}/gain",
                "data_index": 2,
                "write_transform": "wing_headamp_gain_db_to_float",
                "secondary_output": {
                    "_db": {
                        "data_index": 0,
                    },
                },
                "input_padding": {
                    "num_head_amp": 1,
                },
            },
            {
                "tag": "headamps",
                "input": "/io/in/LCL/{num_head_amp}/vph",
                "output": "/headamp/{num_head_amp}/phantom",
                "input_padding": {
                    "num_head_amp": 1,
                },
                "data_type": "boolean",
                "data_index": 2,
            },
            {
                "tag": "headamps",
                "input": "/io/in/LCL/{num_head_amp}/name",
                "output": "/headamp/{num_head_amp}/config_name",
                "input_padding": {
                    "num_head_amp": 1,
                },
            },
            {
                "tag": "headamps",
                "input": "/io/in/LCL/{num_head_amp}/col",
                "output": "/headamp/{num_head_amp}/config_color",
                "input_padding": {
                    "num_head_amp": 1,
                },
                "data_type": "int",
                "data_index": 0,
                "secondary_output": {
                    "_name": {
                        "forward_function": "wing_color_index_to_name",
                        "reverse_function": "wing_color_name_to_index",
                    },
                },
            },

            # Headamps (AES50 A/B/C sources)
            {
                "tag": "headamps",
                "input": "/io/in/A/{num_aes50_in}/g",
                "output": "/headamp/a/{num_aes50_in}/gain",
                "data_index": 2,
                "write_transform": "wing_headamp_gain_db_to_float",
                "secondary_output": {
                    "_db": {
                        "data_index": 0,
                    },
                },
                "input_padding": {
                    "num_aes50_in": 1,
                },
            },
            {
                "tag": "headamps",
                "input": "/io/in/A/{num_aes50_in}/vph",
                "output": "/headamp/a/{num_aes50_in}/phantom",
                "input_padding": {
                    "num_aes50_in": 1,
                },
                "data_type": "boolean",
                "data_index": 2,
            },
            {
                "tag": "headamps",
                "input": "/io/in/A/{num_aes50_in}/name",
                "output": "/headamp/a/{num_aes50_in}/config_name",
                "input_padding": {
                    "num_aes50_in": 1,
                },
            },
            {
                "tag": "headamps",
                "input": "/io/in/A/{num_aes50_in}/col",
                "output": "/headamp/a/{num_aes50_in}/config_color",
                "input_padding": {
                    "num_aes50_in": 1,
                },
                "data_type": "int",
                "data_index": 0,
                "secondary_output": {
                    "_name": {
                        "forward_function": "wing_color_index_to_name",
                        "reverse_function": "wing_color_name_to_index",
                    },
                },
            },
            {
                "tag": "headamps",
                "input": "/io/in/B/{num_aes50_in}/g",
                "output": "/headamp/b/{num_aes50_in}/gain",
                "data_index": 2,
                "write_transform": "wing_headamp_gain_db_to_float",
                "secondary_output": {
                    "_db": {
                        "data_index": 0,
                    },
                },
                "input_padding": {
                    "num_aes50_in": 1,
                },
            },
            {
                "tag": "headamps",
                "input": "/io/in/B/{num_aes50_in}/vph",
                "output": "/headamp/b/{num_aes50_in}/phantom",
                "input_padding": {
                    "num_aes50_in": 1,
                },
                "data_type": "boolean",
                "data_index": 2,
            },
            {
                "tag": "headamps",
                "input": "/io/in/B/{num_aes50_in}/name",
                "output": "/headamp/b/{num_aes50_in}/config_name",
                "input_padding": {
                    "num_aes50_in": 1,
                },
            },
            {
                "tag": "headamps",
                "input": "/io/in/B/{num_aes50_in}/col",
                "output": "/headamp/b/{num_aes50_in}/config_color",
                "input_padding": {
                    "num_aes50_in": 1,
                },
                "data_type": "int",
                "data_index": 0,
                "secondary_output": {
                    "_name": {
                        "forward_function": "wing_color_index_to_name",
                        "reverse_function": "wing_color_name_to_index",
                    },
                },
            },
            {
                "tag": "headamps",
                "input": "/io/in/C/{num_aes50_in}/g",
                "output": "/headamp/c/{num_aes50_in}/gain",
                "data_index": 2,
                "write_transform": "wing_headamp_gain_db_to_float",
                "secondary_output": {
                    "_db": {
                        "data_index": 0,
                    },
                },
                "input_padding": {
                    "num_aes50_in": 1,
                },
            },
            {
                "tag": "headamps",
                "input": "/io/in/C/{num_aes50_in}/vph",
                "output": "/headamp/c/{num_aes50_in}/phantom",
                "input_padding": {
                    "num_aes50_in": 1,
                },
                "data_type": "boolean",
                "data_index": 2,
            },
            {
                "tag": "headamps",
                "input": "/io/in/C/{num_aes50_in}/name",
                "output": "/headamp/c/{num_aes50_in}/config_name",
                "input_padding": {
                    "num_aes50_in": 1,
                },
            },
            {
                "tag": "headamps",
                "input": "/io/in/C/{num_aes50_in}/col",
                "output": "/headamp/c/{num_aes50_in}/config_color",
                "input_padding": {
                    "num_aes50_in": 1,
                },
                "data_type": "int",
                "data_index": 0,
                "secondary_output": {
                    "_name": {
                        "forward_function": "wing_color_index_to_name",
                        "reverse_function": "wing_color_name_to_index",
                    },
                },
            },
        ]
        # Bus -> Bus Sends
        # Note: Sending bus 'n' to bus 'n' is NOT possible and is ignored.
        # bus->bus send mappings without self-sends.
        for bus in range(1, self.num_bus + 1):
            for send in range(1, self.num_bus_send + 1):
                if send == bus:
                    continue
                self.extra_addresses_to_load.extend(
                    [
                        {
                            "tag": "busbussends",
                            "input": f"/bus/{bus}/send/{send}/on",
                            "output": f"/busbussend/{bus}/{send}/mix_on",
                            "data_type": "boolean",
                            "data_index": 2,
                        },
                        {
                            "tag": "busbussends",
                            "input": f"/bus/{bus}/send/{send}/lvl",
                            "output": f"/busbussend/{bus}/{send}/mix_fader",
                            "write_transform": "fader_to_db",
                            "data_index": 1,
                            "secondary_output": {"_db": {"data_index": 0}},
                        },
                        {
                            "tag": "busbussends",
                            "input": f"/bus/{bus}/send/{send}/pre",
                            "output": f"/busbussend/{bus}/{send}/pre",
                            "data_type": "boolean",
                            "data_index": 2,
                        },
                    ]
                )

        super().__init__(**kwargs)
