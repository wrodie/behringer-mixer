# behringer-mixer
Python module to get basic information from Behringer digital mixers eg X32/XAir etc.

Initial inspiration (and some code) comes from https://github.com/onyx-and-iris/xair-api-python.

## What it does and what it doesn't do.
This module is a simple interface to a series of Behringer digital mixers.  It does NOT support all parameters or controls.  It is primarily focussed on getting and setting fader information.  It supports getting this information, both on a once off basis and subscribing for real-time updates.

It currently supports the following functionality for all channels/busses/matrices/dcas/main/lr:
- Fader Value (float and dB) [get/set]
- Fader Mute status(float and dB) [get/set]
- Fader Name (float and dB) [get]

It also supports
- Current scene/snapshot [get]
- Change scene/snapshot [set]

If you want a module that allows you to control the full functionality of the mixer, eg configuring effects/eq etc then I would recommend checking out https://github.com/onyx-and-iris/xair-api-python instead.

## Prerequisites

-   Python 3.10 or greater

<!--## Installation

```
pip install behringer-mixer
```
-->

## Usage


### Example
```python

from behringer_mixer import mixer_api

def updates_function(data):
    print(f"The property {data.property} has been set to {data.value}")

def main():
    with mixer_api.connect("X32", ip="192.168.201.149") as mixer:
        state = mixer.state()
        print(state)
        mixer.subscribe(updates_function)
        mixer.set_value("/ch/1/mix_fader", 0)

if __name__ == "__main__":
    main()
```

### Property Keys
The data returned by both the `state` and `subscription` callback function is based on a number of property keys for the mixer.  While these keys are 'similar' to the values used in the OSC commands they are not always the same.

Each key is a mixture of a base 'group' key eg `/ch/1/` and a more specific key.  
They keys have also been altered slightly to maintain a consistent approach between different mixers. eg. For channel/bus numbers the leading zero has been removed. on the XAir mixers the main fader is `/main/lr` whereas on the X32 it is `/main/st`.  This modules returns both as `/main/st`.

#### `mixer_api.connect("<mixer_type>", ip="<ip_address>")`
The code is written to support the following mixer types:
- `X32`
- `XR18`
- `XR16`
- `XR12`
(I currently only have access to an X32.)

The following keyword arguments may be passed:

-   `ip`: ip address of the mixer
-   `port`: mixer port, defaults to 10023 for x32 and 10024 for xair
-   `delay`: a delay between each command, defaults to 20ms.
    -   a note about delay, stability may rely on network connection. For wired connections the delay can be safely reduced.  

On connection, the function requests the current state of the appropriate faders from the mixer.  This results in a number of OSC messages being sent.  If you have problems receiving all this data, then tweaking the delay setting may be appropriate.

#### `mixer.state()`
Returns the current state of the mixer as a dictionary of values
```
{
	'/ch/1/mix_fader': 0.75,
	'/ch/1/mix_fader_db': 0.0,
    ...
	'/ch/1/mix_on': False,
	'/ch/2/mix_on': False,
	'/ch/1/config_name': 'VOX 1',
	...
	'/bus/1/mix_fader': 0.37829911708831787,
	'/bus/1/mix_fader_db': -19.7,
	...
	'/bus/4/mix_on': True,
	...
	'/bus/2/config_name': '',
	...
	'/dca/3/config_name': 'Drums',
	...
	'/main/st/mix_fader': 0.7497556209564209,
	'/main/st/mix_fader_db': -0.0,
	'/main/st/mix_on': True,
	...
	'/scene/current': 6
}
```

#### `mixer.reload()`
Causes the the mixer to be requeried for it's current state. This only updates the modules internal state.  You would then need to call `mixer.state()` to receive the updated state.

#### `mixer.subscribe(callback_function)`
This registered a `callback_function` that is called whenever there is a change at the mixer on one of the monitored properties.
The callback function must receive one dictionary parameter that contains the data that has been updated.
The content of this data paramter is as follows

```python
{ 
    'property': '/ch/01/mix_fader',
    'value': 0.85
}
```

Updates will automatically be stopped when the code passes outside the `with` context.

#### `mixer.set_value(address, value)`
Tells the mixer to update a particular field parameter to the `value` specified.
`address` should be in the format returned by the `mixer.state()` call.
`value should be in a format appropriate to the address being used. The module does no checking on the appropriateness of the value.
This call also updates the internal state of the module.

#### `mixer.load_scene(scene_number)`
Changes the current/scene snapshot of the mixer.
`scene_number` is the index

#### `mixer.send(address, value)` (Low Level Call)
This is a low level call to send an OSC message to the mixer.  As this is a low level call, the address of the OSC message being sent would have to conform to that required by the mixer in its documenation, no changing of the address is performed.  This call does not update the internal state

#### `mixer.query(address)` (Low Level Call)
This is a low level call and returns the response of a previous `send` call.



## Tests

These tests attempt to connect to a mixer to exercise get/set from the channels.
The tests will change the state of the mixer, so it is recommended you save the current settings before running.
It is also recommended that any amplifier is turned off as feedback could occur if signals are present on the channels.

To run all tests:

`pytest -v`.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Documentation

[XAir OSC Commands](https://behringer.world/wiki/doku.php?id=x-air_osc)

[X32 OSC Commands](https://wiki.munichmakerlab.de/images/1/17/UNOFFICIAL_X32_OSC_REMOTE_PROTOCOL_%281%29.pdf)

## Special Thanks

[Onyx-and-Iris](https://github.com/onyx-and-iris) for writing the XAir Python module
