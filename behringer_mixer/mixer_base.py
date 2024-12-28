""" Base module for the mixer """

import asyncio
import logging
import time
from typing import Optional
from pythonosc.dispatcher import Dispatcher
from .errors import MixerError
from . import utils
from .mixer_osc import OSCClientServer
from .mappings import build_mappings


class MixerBase:
    """Handles the communication with the mixer via the OSC protocol"""

    logger = logging.getLogger("behringermixer.behringermixer")

    _CONNECT_TIMEOUT = 0.5

    _info_response = []
    port_number: int = 10023
    # delay: float = 0.000
    addresses_to_load = []
    cmd_scene_load = ""
    tasks = set()
    _mixer_status = {
        "ip_address": None,
        "name": None,
        "type": None,
        "firmware": None,
    }

    def __init__(self, **kwargs):
        self.ip = kwargs.get("ip")
        self.port = kwargs.get("port") or self.port_number
        self._delay = kwargs.get("delay", 0) if "delay" in kwargs else self.delay
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(kwargs.get("logLevel") or logging.WARNING)
        if not self.ip:
            raise MixerError("No valid ip detected")

        self._callback_function = None
        self.subscription = None
        self._state = {}
        self._mappings_reverse = {}
        self.server = None
        self._last_received = 0
        self._subscription_status_callback = None
        self._subscription_status_connection = False

        (self._mappings, self._secondary_mappings) = build_mappings(self)
        self._build_reverse_mappings()

    async def validate_connection(self):
        """Validate connection to the mixer"""
        await self.send("/xinfo")
        await asyncio.sleep(self._CONNECT_TIMEOUT)
        if not self.info_response:
            self.logger.debug(
                "Failed to setup OSC connection to mixer. Please check for correct ip address."
            )
            return False

        self.logger.debug(
            "Successfully connected to %s at %s.",
            {self.info_response[2]},
            {self.info_response[0]},
        )
        return True

    @property
    def info_response(self):
        """Return any OSC responses"""
        return self._info_response

    async def start(self):
        """Startup the server"""
        if not self.server:
            dispatcher = Dispatcher()
            dispatcher.set_default_handler(self.msg_handler)
            self.server = OSCClientServer(
                (self.ip, self.port), dispatcher, asyncio.get_event_loop()
            )
            transport, protocol = await self.server.create_serve_endpoint()
            self.server.register_transport(transport, protocol)
        return await self.validate_connection()

    def msg_handler(self, addr, *data):
        """Handle callback response"""

        self.logger.debug(f"received: {addr} {data if data else ''}")
        self._last_received = time.time()
        updates = self._update_state(addr, data)
        if addr == "/xinfo":
            self.handle_xinfo(data)
            updates = []
        if self._callback_function:
            for row in updates:
                self._callback_function(row)
        else:
            self._info_response = data[:]

    async def send(self, addr: str, param: Optional[str] = None):
        """Send an OSC message"""
        self.logger.debug(f"sending: {addr} {param if param is not None else ''}")
        self.server.send_message(addr, param)
        self._info_response = None
        await asyncio.sleep(self._delay)

    async def query(self, address):
        """Send an receive the value of an OSC message"""
        await self.send(address)
        return self.info_response

    async def subscribe(self, callback_function):
        """run the subscribe worker"""
        await self._subscribe_worker("/xremote", callback_function)

    async def _subscribe_worker(self, parameter_string, callback_function):
        """Worker to handle subscription and renewal of OSC messages."""
        self._callback_function = callback_function
        await self.send(parameter_string)
        renew_string = "/renew"
        if parameter_string == "/xremote":
            renew_string = "/xremote"
        self._subscription_status_connection = True
        while self._callback_function:
            await asyncio.sleep(9)
            await self.send(renew_string)
            await self.send("/xinfo")
            if self.subscription_connected() != self._subscription_status_connection:
                self._subscription_status_connection = (
                    True if self.subscription_connected() else False
                )
                if self._subscription_status_connection:
                    # Coming back from loss of connection, need to reload state
                    await self.reload()
                if self._subscription_status_callback:
                    self._subscription_status_callback(
                        self._subscription_status_connection
                    )

        return True

    async def unsubscribe(self):
        """Stop the subscription"""
        await self.send("/unsubscribe")
        self._callback_function = None
        return True

    async def stop(self):
        """Stop the OSC server"""
        self.server.shutdown()
        return True

    def state(self, key=None):
        """Return current mixer state"""
        if key:
            return self._state.get(key)
        return self._state

    async def load_scene(self, scene_number):
        """Load a new scene on the mixer"""
        await self.send(self.cmd_scene_load, scene_number)
        # Because of potential UDP buffer overruns (lots of messages are sent on
        # a scene change), data may be lost
        # therefore we need to wait for the scene change to finish
        # and then update the state to make sure we have everything
        await asyncio.sleep(1)
        await self._load_initial()

    async def reload(self):
        """Reload state"""
        self._state = {}
        await self._load_initial()

    async def _load_initial(self):
        """Load initial state"""
        for address in self._mappings.keys():
            await self.send(address)

    def _update_state(self, address, values):
        """Update internal state representation, called when a message is received"""
        if address not in self._mappings:
            return []
        address_data = self._mappings[address]
        state_key = address_data.get("output")
        value = values[0]
        if len(values) > 1:
            value = values
        updates = []
        if state_key:
            if address_data.get("mapping"):
                value = address_data["mapping"].get(value)
            if address_data.get("data_type", "") == "boolean":
                value = bool(value)
            self._state[state_key] = value
            updates.append({"property": state_key, "value": value})
            for suffix, secondary_data in address_data.get(
                "secondary_output", {}
            ).items():
                secondary_key = state_key + suffix
                new_value = getattr(utils, secondary_data["forward_function"])(value)
                self._state[secondary_key] = new_value
                updates.append({"property": secondary_key, "value": new_value})
        return updates

    def _build_reverse_mappings(self):
        """Invert the mapping for self._mappings"""
        if not self._mappings_reverse:
            self._mappings_reverse = {v["output"]: v for v in self._mappings.values()}

    async def set_value(self, address, value):
        """Set the value in the mixer"""
        if address in self._secondary_mappings:
            address_data = self._mappings.get(self._secondary_mappings[address])
            for suffix, secondary_data in address_data.get(
                "secondary_output", {}
            ).items():
                if address.endswith(suffix):
                    value = getattr(utils, secondary_data["reverse_function"])(value)
                    address = address_data.get("output")
                    break
        if value is False:
            value = 0
        if value is True:
            value = 1
        if address_data.get("mapping"):
            reverse_map = {v: k for k, v in address_data["mapping"].items()}
            value = reverse_map[value]
        await self.send(address_data["input"], value)
        await self.query(address_data["input"])

    def last_received(self):
        """Return the timestamp of the last time the module received a message from the mixer"""
        return self._last_received

    def subscription_connected(self):
        """Return true if the module has received a message from the mixer in the last 15 seconds"""
        return False if (time.time() - self._last_received) > 15 else True

    async def subscription_status_register(self, callback_function):
        """Register a callback function that is called each time the status of the subscription changes"""
        self._subscription_status_callback = callback_function
        return True

    def name(self):
        """Return the name of the mixer"""
        return self._mixer_status.get("name")

    def firmware(self):
        """Return the firmware version of the mixer"""
        return self._mixer_status.get("firmware")

    def handle_xinfo(self, data):
        """Handle the return data from xinfo requests"""
        self._mixer_status = {
            "ip_address": data[0],
            "name": data[1],
            "type": data[2],
            "firmware": data[3],
        }

    def dump_mapping(self):
        """Dump the mapping table"""
        output = []
        for original_path in sorted(self._mappings.keys()):
            output.append((original_path, self._mappings[original_path]["output"]))
        return output
