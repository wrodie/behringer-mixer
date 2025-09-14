""" Base module for the mixer """

from typing import Optional, Callable, Dict, Any, List
import asyncio
import logging
import time
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
        """Initialize the mixer"""
        self.ip = kwargs.get("ip")
        self.port = kwargs.get("port") or self.port_number
        self._delay = kwargs.get("delay", 0) if "delay" in kwargs else self.delay
        if kwargs.get("logger"):
            self.logger = kwargs.get("logger")
        else:
            self.logger.addHandler(logging.StreamHandler())
            self.logger.setLevel(kwargs.get("logLevel") or logging.WARNING)
        self.include = kwargs.get("include") or []
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
        self.extra_addresses_to_load = self.extra_addresses_to_load or []
        (self._mappings, self._secondary_mappings) = build_mappings(self)
        self._build_reverse_mappings()

    async def validate_connection(self):
        """Validate connection to the mixer"""
        await self.send(self.info_address)
        await asyncio.sleep(self._CONNECT_TIMEOUT)
        if not self.info_response:
            self.logger.debug(
                "Failed to setup OSC connection to mixer. Please check for correct ip address."
            )
            return False
        self.logger.debug(
            "Successfully connected to %s at %s.",
            self._mixer_status.get("name"),
            self._mixer_status.get("ip_address"),
        )
        return True

    @property
    def info_response(self):
        """Return any OSC responses"""
        return self._info_response

    async def start(self):
        """Startup the server"""
        if not self.server:
            self.server = OSCClientServer(
                (self.ip, self.port), self.msg_handler, asyncio.get_event_loop()
            )
            transport, protocol = await self.server.create_serve_endpoint()
            self.server.register_transport(transport, protocol)
        return await self.validate_connection()

    def msg_handler(self, addr, *data):
        """Handle callback response"""

        self.logger.debug(f"received: {addr} {data if data else ''}")
        self.logger.debug(f"received: a={addr} d={data if data else ''}")
        self._last_received = time.time()
        updates = self._update_state(addr, data)
        if addr == "/xinfo":
            self.handle_xinfo(data)
            updates = []
        if addr == "/*":
            self.handle_winfo(data)
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
        await self._subscribe_worker(self.subscription_string, callback_function)

    async def _subscribe_worker(self, parameter_string, callback_function):
        """Worker to handle subscription and renewal of OSC messages."""
        self._callback_function = callback_function
        await self.send(parameter_string)
        renew_string = self.subscription_renew_string
        if parameter_string == self.subscription_string:
            renew_string = self.subscription_string
        self._subscription_status_connection = True
        while self._callback_function:
            await asyncio.sleep(9)
            await self.send(renew_string)
            await self.send(self.info_address)
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
        await self.send(self.cmd_scene_load, str(scene_number))
        if self.cmd_scene_execute:
            await self.send(self.cmd_scene_execute[0], self.cmd_scene_execute[1])
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

    def _update_state(self, address: str, values: List[Any]) -> List[Dict[str, Any]]:
        """Update internal state representation, called when a message is received
        Args:
            address (str): The address to update.
            values (List[Any]): The values to update.

        Returns:
            List[Dict[str, Any]]: A list of updates.
        """
        if address not in self._mappings:
            return []
        address_data = self._mappings.get(address, {})
        state_key = address_data.get("output")
        value = values[0] if len(values) == 1 else values
        updates = []
        if state_key:
            if "data_index" in address_data:
                value = values[address_data["data_index"]]
            if address_data.get("mapping"):
                value = address_data["mapping"].get(value)
            if address_data.get("data_type", "") == "boolean":
                value = bool(value)
            if address_data.get("data_type", "") == "boolean_inverted":
                value = not bool(value)
            self._state[state_key] = value
            updates.append({"property": state_key, "value": value})
            for suffix, secondary_data in address_data.get(
                "secondary_output", {}
            ).items():
                secondary_key = state_key + suffix
                secondary_value = value
                if "data_index" in secondary_data:
                    secondary_value = values[secondary_data["data_index"]]
                if "forward_function" in secondary_data:
                    secondary_value = getattr(
                        utils, secondary_data["forward_function"]
                    )(secondary_value, address_data)
                self._state[secondary_key] = secondary_value
                updates.append({"property": secondary_key, "value": secondary_value})
        return updates

    def _build_reverse_mappings(self) -> None:
        """Invert the mapping for self._mappings."""
        if not self._mappings_reverse:
            self._mappings_reverse = {v["output"]: v for v in self._mappings.values()}

    async def set_value(self, address: str, value: Any) -> None:
        """Set the value in the mixer

        Args:
            address (str): The address to process.
            value (Any): The value to process.
        """
        address_data = None
        if address in self._secondary_mappings:
            address_data = self._mappings.get(self._secondary_mappings[address])
            for suffix, secondary_data in address_data.get(
                "secondary_output", {}
            ).items():
                if address.endswith(suffix):
                    value = getattr(utils, secondary_data["reverse_function"])(
                        value, address_data
                    )
                    address = address_data.get("output")
                    break
        if not address_data:
            address_data = self._mappings_reverse.get(address) or {}

        if address_data.get("data_type", "") == "boolean_inverted":
            value = not value
        if value is False:
            value = 0
        if value is True:
            value = 1
        if "write_transform" in address_data:
            value = getattr(utils, address_data["write_transform"])(value, address_data)
            value = str(value)
        if address_data.get("mapping"):
            reverse_map = {v: k for k, v in address_data["mapping"].items()}
            value = reverse_map[value]
        if address_data:
            await self.send(address_data["input"], value)
            await self.query(address_data["input"])

    def last_received(self) -> float:
        """Return the timestamp of the last time the module received a message from the mixer.

        Returns:
            float: The timestamp of the last received message.
        """
        return self._last_received

    def subscription_connected(self) -> bool:
        """Return true if the module has received a message from the mixer in the last 15 seconds.

        Returns:
            bool: True if connected, False otherwise.
        """
        return (time.time() - self._last_received) <= 15

    async def subscription_status_register(
        self, callback_function: Callable[[bool], None]
    ) -> bool:
        """Register a callback function that is called each time the status of the subscription changes.

        Args:
            callback_function (Callable[[bool], None]): The callback function to register.

        Returns:
            bool: True if registration is successful.
        """
        self._subscription_status_callback = callback_function
        return True

    def name(self) -> Optional[str]:
        """Return the name of the mixer.

        Returns:
            Optional[str]: The name of the mixer.
        """
        return self._mixer_status.get("name")

    def firmware(self) -> Optional[str]:
        """Return the firmware version of the mixer.

        Returns:
            Optional[str]: The firmware version of the mixer.
        """
        return self._mixer_status.get("firmware")

    def handle_xinfo(self, data: List[Any]) -> None:
        """Handle the return data from xinfo requests.

        Args:
            data (List[Any]): The data received from the xinfo request.
        """
        self._mixer_status = {
            "ip_address": data[0],
            "name": data[1],
            "type": data[2],
            "firmware": data[3],
        }

    def handle_winfo(self, data: List[Any]) -> None:
        """Handle the return data from /? requests.

        Args:
            data (List[Any]): The data received from the xinfo request.
        """
        values = data[0].split(",")
        self._mixer_status = {
            "ip_address": values[1],
            "name": values[2],
            "type": values[3],
            "firmware": values[5],
        }

    def dump_mapping(self) -> List[Dict[str, str]]:
        """Dump the mapping table.

        Returns:
            List[Dict[str, str]]: The dumped mapping table.
        """
        output = []
        for original_path in sorted(self._mappings.keys()):
            output.append(
                {
                    "input": original_path,
                    "output": self._mappings[original_path]["output"],
                }
            )
        return output
