""" Base module for the mixer """
import re
import asyncio
import logging
import time
from typing import Optional
from pythonosc.dispatcher import Dispatcher
from .errors import MixerError
from .utils import fader_to_db, db_to_fader
from .mixer_osc import OSCClientServer


class MixerBase:
    """Handles the communication with the mixer via the OSC protocol"""

    logger = logging.getLogger("behringermixer.behringermixer")

    _CONNECT_TIMEOUT = 0.5

    _info_response = []
    port_number: int = 10023
    #delay: float = 0.000
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
        self._mappings = {}
        self._data_mappings = {}
        self._mappings_reverse = {}
        self._valid_addresses = {}
        self.server = None
        self._last_received = 0
        self._subscription_status_callback = None
        self._subscription_status_connection = False

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
        expanded_addresses = []
        for address_row in self.addresses_to_load:
            (new_expanded_address_list, new_mappings) = self._expand_address(
                address_row
            )
            expanded_addresses = expanded_addresses + new_expanded_address_list
            self._mappings.update(new_mappings)

        for address in expanded_addresses:
            self._valid_addresses[address] = True
            await self.send(address)

    def _expand_address(self, address_tuple):
        # Expand an address including wildcards
        expanded_addresses = []
        mappings = {}
        processlist = [address_tuple]
        while processlist:
            row = processlist.pop(-1)
            address = row[0]
            rewrite_address = row[1] if len(row) > 1 else None
            data_mapping = row[2] if len(row) > 2 else None
            matches = re.search(r"\{(.*?)(:(\d)){0,1}\}", address)
            if matches:
                match_var = matches.group(1)
                max_count = getattr(self, match_var)
                zfill_num = int(matches.group(3) or 0) or len(str(max_count))
                for number in range(1, max_count + 1):
                    new_rewrite_address = ""
                    mapping_address = address
                    new_address = address.replace(
                        "{" + match_var + str(matches.group(2) or "") + "}",
                        str(number).zfill(zfill_num),
                    )
                    mapping_address = mapping_address.replace(
                        "{" + match_var + str(matches.group(2) or "") + "}", str(number)
                    )
                    if rewrite_address:
                        mapping_address = rewrite_address.replace(
                            "{" + match_var + str(matches.group(2) or "") + "}",
                            str(number),
                        )
                        # str(number).zfill(zfill_num),
                    processlist.append([new_address, mapping_address, data_mapping])
            else:
                expanded_addresses.append(address)
                mapping_address = rewrite_address if rewrite_address else address
                mapping_address = re.sub(
                    r"(\d+/[^\d]+)(/)([^\d]+)$", "\g<1>_\g<3>", mapping_address
                )
                if data_mapping:
                    self._data_mappings[address] = data_mapping
                if mapping_address != address:
                    mappings[address] = mapping_address
        return (expanded_addresses, mappings)

    def _update_state(self, address, values):
        # update internal state representation
        # State looks like
        #    /ch/2/mix_fader = Value
        #    /ch/2/config_name = Value
        if not address in self._valid_addresses:
            return []
        state_key = self._mappings.get(address) or address
        value = values[0]
        if len(values) > 1:
            value = values
        updates = []
        if state_key:
            if self._data_mappings.get(address):
                value = self._data_mappings[address].get(value)
            if state_key.endswith("_on") or state_key.endswith("/on"):
                value = bool(value)
            state_key = re.sub(r"/0+(\d+)/", r"/\1/", state_key)
            self._state[state_key] = value
            updates.append({"property": state_key, "value": value})
            if state_key.endswith("_fader"):
                db_val = fader_to_db(value)
                self._state[state_key + "_db"] = db_val
                updates.append({"property": state_key + "_db", "value": db_val})
        return updates

    def _build_reverse_mappings(self):
        # Invert the mapping for self._mappings
        if not self._mappings_reverse:
            self._mappings_reverse = {v: k for k, v in self._mappings.items()}

    async def set_value(self, address, value):
        """Set the value in the mixer"""
        if address.endswith("_db"):
            address = address.replace("_db", "")
            value = db_to_fader(value)
        if value is False:
            value = 0
        if value is True:
            value = 1
        self._build_reverse_mappings()
        true_address = self._mappings_reverse.get(address) or address
        if self._data_mappings.get(true_address):
            reverse_map = {v: k for k, v in self._data_mappings[true_address].items()}
            value = reverse_map.get(value)
        await self.send(true_address, value)
        await self.query(true_address)

    def _redo_padding(self, address):
        # Go through address and see if it matches with one of the known address
        # if so, make sure the numbers are padded correctly

        for address_row in self.addresses_to_load:
            initial_address = address_row[0]
            matches = re.search(r"^(.*)/{(num_[a-z]+?)(:(\d)){0,1}}", initial_address)
            if matches:
                init_string = matches.group(1)
                if address.startswith(init_string):
                    max_count = getattr(self, matches.group(2))
                    zfill_num = int(matches.group(4) or 0) or len(str(max_count))
                    sub_match = re.search(r"^" + init_string + r"/(\d+)/", address)
                    num = sub_match.group(1)
                    address = address.replace(
                        f"{init_string}/{num}/",
                        f"{init_string}/" + str(num).zfill(zfill_num) + "/",
                    )
        return address

    def last_received(self):
        # Return the timestamp of the last time the module received a message from the mixer
        return self._last_received

    def subscription_connected(self):
        # Return true if the module has received a message from the mixer in the last 15 seconds
        return False if (time.time() - self._last_received) > 15 else True

    async def subscription_status_register(self, callback_function):
        # register a callback function that is called each time the status of the subscription changes
        self._subscription_status_callback = callback_function
        return True

    def name(self):
        # Return the name of the mixer
        return self._mixer_status.get("name")

    def firmware(self):
        # Return the firmware version of the mixer
        return self._mixer_status.get("firmware")

    def handle_xinfo(self, data):
        # Handle the return data from xinfo requests
        self._mixer_status = {
            "ip_address": data[0],
            "name": data[1],
            "type": data[2],
            "firmware": data[3],
        }
