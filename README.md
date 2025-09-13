# behringer-mixer
Python module to get basic information from Behringer digital mixers eg X32/Wing/XAir etc.

Initial inspiration (and some code) comes from https://github.com/onyx-and-iris/xair-api-python.

## What it does and what it doesn't do.
This module is a simple interface to a series of Behringer digital mixers.  It does NOT support all parameters or controls.  It is primarily focussed on getting and setting fader information.  It supports getting this information, both on a once off basis and subscribing for real-time updates.

It currently supports the following functionality for all channels/busses/matrices/auxin/dcas/main/lr/mono:
- Fader Value (float and dB) [get/set]
- Fader Color (index 0-15 and color name) [get/set]
- Fader Mute status [get/set]
- Fader Name [get]

It also supports
- Current scene/snapshot [get]
- Change scene/snapshot [set]
- Control USB Player/Recorder [get/set]
- Current USB Filename [get]
- Firmware version
- Control of head-amps gain/phantom power
- Mute groups

If you want a module that allows you to control the full functionality of the mixer, eg configuring effects/eq etc then I would recommend checking out https://github.com/onyx-and-iris/xair-api-python instead. Or if you have a focus on the X-Series, you could also look at https://github.com/matiasbarrios/magical-mixers/.

## Prerequisites

-   Python 3.10 or greater

## Installation

```
pip install behringer-mixer
```

## Usage

This module depends on the asyncio module to handle multiple runnings tasks simultaneously.

### Example
```python
import asyncio
import logging
from behringer_mixer import mixer_api

def updates_function(data):
    print(f"The property {data.get('property')} has been set to {data.get('value')}")

async def main():
    mixer  = mixer_api.create("X32", ip="192.168.201.149", logLevel=logging.WARNING)
    await mixer.start()
    state = await mixer.reload()
    state = mixer.state()
    print(state)
    asyncio.create_task(mixer.subscribe(updates_function))
    await mixer.set_value("/ch/1/mix_fader", 10)
    await asyncio.sleep(20)

if __name__ == "__main__":
    asyncio.run(main())
```

### Property Keys
The data returned by both the `state` and `subscription` callback function is based on a number of property keys for the mixer.  While these keys are 'similar' to the values used in the OSC commands they are not always the same.

Each key is a mixture of a base 'group' key eg `/ch/1/` and a more specific key.  
They keys have also been altered slightly to maintain a consistent approach between different mixers. eg. For channel/bus numbers the leading zero has been removed. on the XAir mixers the main fader is `/main/lr` whereas on the X32 it is `/main/st`.  This modules returns both as `/main/st`.

#### `mixer_api.create("<mixer_type>", ip="<ip_address>")`
The code is written to support the following mixer types:
- `X32`
- `XR18`
- `XR16`
- `XR12`
- `WING`

The following keyword arguments may be passed:

-   `ip`: ip address of the mixer (Required)
-   `port`: mixer port, defaults to 10023 for x32 and 10024 for xair
-   `delay`: a delay between each command, defaults to 20ms.
    -   a note about delay, stability may rely on network connection. For wired connections the delay can be safely reduced.  
-   `logLevel`: the level of logging, defaults to warning (enums from logging eg logging.DEBUG)
-   `include`: Optional. A list of what types of data to include. eg ["channels","bussess"] If not included then ALL data is returned.   Valid values are:
    - `channels`
    - `channelsends`
    - `auxins`
    - `busses`
    - `bussends`
    - `busmainsends`
    - `matrices`
    - `dcas`
    - `headamps`
    - `mains`
    - `mono`
    - `show`
    - `usb`
    - `mutegroups`

The create function only creates an instance of the mixer, it does not 'connect' to it.
You should call the `mixer.start()` function to prepare communication and then call `mixer.validate_connection()` to check that the connection to the mixer worked.

#### `mixer.firmware()`
Returns the firmware version of the mixer.
`
#### `mixer.info()`
Returns information about the mixer, giving the number of channels/busses etc as well as the base part of the 'address' for that component.
```
        {
            "channel": {
                "number": 32,
                "base_address": "ch",
            },
            "bus": {
                "number": 16,
                "base_address": "bus",
            },
            "matrix": {
                "number": 6,
                "base_address": "mtx",
            },
            "dca": {
                "number": 8,
                "base_address": "dca",
            },
            "fx": {
                "number": 10,
                "base_address": "fx",
            },
            "auxrtn": {
                "number": 8,
                "base_address": "auxrtn",
            },
            "scenes": {
                "number": 100,
                "base_address": "scene",
            },
        }
```

#### `mixer.last_received()`
Returns a unix timestamp giving the last time data was received from the mixer.

#### async `mixer.load_scene(scene_number)`
Changes the current/scene snapshot of the mixer.
`scene_number` is the scene number as stored on the mixer.

#### `mixer.name()`
Returns the network name of the mixer.

#### async `mixer.query(address)` (Low Level Call)
This is a low level call and returns the response of a previous `send` call. You should not need to call this, but rely on the managed state instead.

#### async `mixer.reload()`
Causes the the mixer to be requeried for it's current state. This only updates the module's internal state.  You would then need to call `mixer.state()` to receive the updated state.

#### async `mixer.send(address, value)` (Low Level Call)
This is a low level call to send an OSC message to the mixer.  As this is a low level call, the address of the OSC message being sent would have to conform to that required by the mixer in its documenation, no changing of the address is performed.  This call does not update the internal state. You should not need to call this, but rely on the managed state instead.

#### async `mixer.set_value(address, value)`
Tells the mixer to update a particular field parameter to the `value` specified.
`address` should be in the format returned by the `mixer.state()` call.
`value` should be in a format appropriate to the address being used. The module does no checking on the appropriateness of the value.
This call also updates the internal state of the module.

#### async `mixer.start()`
Starts the OSC server to process messages. Data will not be returned/processed unless this has been run

#### `mixer.state(<address>)`
Returns the current state of the mixer. If the optional address parameter is provided then the current state of that address is returned.  If the parameter is not provided then the entire state is returned as a dictionary of values.
```
{
	'/ch/1/mix_fader': 0.75,
	'/ch/1/mix_fader_db': 0.0,
    ...
	'/ch/1/mix_on': False,
	'/ch/2/mix_on': False,
	'/ch/1/config_name': 'VOX 1',
	'/ch/1/config_color': 4,
	'/ch/1/config_color_name': 'BL',
	...
	'/bus/1/mix_fader': 0.37829911708831787,
	'/bus/1/mix_fader_db': -19.7,
	...
	'/bus/4/mix_on': True,
	...
	'/bus/2/config_name': '',
	...
	'/dca/3/config_name': 'Drums',
	'/dca/3/config_color': 10,
	'/dca/3/config_color_name': 'GNi',
	...
	'/main/st/mix_fader': 0.7497556209564209,
	'/main/st/mix_fader_db': -0.0,
	'/main/st/mix_on': True,
	...
	'/scene/current': 6
}
```

#### async `mixer.stop()`
Stops the OSC server and the ability to process messages

#### async `mixer.subscribe(callback_function)`
This registers a `callback_function` that is called whenever there is a change at the mixer on one of the monitored properties.
The callback function will receive one dictionary parameter that contains the data that has been updated.
The content of this data parameter is as follows

```python
{ 
    'property': '/ch/01/mix_fader',
    'value': 0.85
}
```

#### async `mixer.subscription_connected()`
Returns true if the module has received data from the mixer in the last 15 seconds. 

#### async `mixer.subscription_status_register(callback_function)`
Register a function to be called when the subscription status changes.  This function is called when `subscription_connected()` changes.

#### async `mixer.unsubscribe()`
Stops the module listening to real time updates

#### async `mixer.validate_connection()`
Returns `True` if the connection to the mixer is successful, `False` otherwise.

## Caveats
### Behringer Wing Support
Behringer Wing support is new and the Wing is quite different to how the other X/M/X series mixers work. Not all the functionality of the the other mixers is supported with the wing currently:
 - No Headamp support
 - No USB recorder support - USB player is supported
 - Bus->Bus send controls (Bus to Matrix/Main is supported)

I don't believe any of these are impossible to achieve, just because they are tricker and I haven't put in the time yet.  I'm not even sure if they are needed.

**WARNING** - This module makes use of OSC subscription to get updated values of controls.  Differently to the X-Series mixers the Wing only supports one client to receive this data at a time.  So this means if you are using another integration that makes use of this same OSC subscription on the mixer, eg [Bitfocus Companion](https://bitfocus.io/companion), then they will compete for the same connection and both won't work properly.  I believe other software such as Wing Edit/WingQ/Mixing Station make use of a different protocol and don't suffer with this problem.


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

[Wing OSC Commands](https://wing-docs.com/pdf/OSC_Documentation.pdf)

[Patrick-Gilles Maillot](https://sites.google.com/site/patrickmaillot/wing)
## Special Thanks

[Onyx-and-Iris](https://github.com/onyx-and-iris) for writing the XAir Python module
