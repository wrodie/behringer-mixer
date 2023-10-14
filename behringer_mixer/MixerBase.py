import re
import logging
import threading
import time
from .errors import MixerError
from typing import Optional, Union
from .utils import fader_to_db, db_to_fader
from .mixer_osc import OSCClientServer
from pythonosc.dispatcher import Dispatcher


class MixerBase:
    """Handles the communication with the mixer via the OSC protocol"""

    logger = logging.getLogger("beheringermixer.behringermixer")

    _CONNECT_TIMEOUT = 0.5

    _info_response = []

    def __init__(self, **kwargs):
        self.ip = kwargs.get("ip")
        self.port = kwargs.get("port") or self.port_number
        self._delay = kwargs.get("delay") or self.delay
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(kwargs.get("logLevel") or logging.WARNING)
        if not self.ip:
            raise MixerError("No valid ip detected")

        dispatcher = Dispatcher()
        dispatcher.set_default_handler(self.msg_handler)
        self._callback_function = None
        self.subscription = None
        self._state = {}
        self._rewrites = {}
        self._rewrites_reverse = {}
        self.server = OSCClientServer((self.ip, self.port), dispatcher)

    def __enter__(self):
        self.worker = threading.Thread(target=self.run_server, daemon=True)
        self.worker.start()
        self.validate_connection()
        return self

    def validate_connection(self):
        self.send("/xinfo")
        time.sleep(self._CONNECT_TIMEOUT)
        if not self.info_response:
            raise MixerError(
                "Failed to setup OSC connection to mixer. Please check for correct ip address."
            )
        print(
            f"Successfully connected to {self.info_response[2]} at {self.info_response[0]}."
        )

    @property
    def info_response(self):
        return self._info_response

    def run_server(self):
        self.server.serve_forever()

    def msg_handler(self, addr, *data):
        self.logger.debug(f"received: {addr} {data if data else ''}")
        updates = self._update_state(addr, data)
        if self._callback_function:
            for row in updates:
                self._callback_function(row)
        else:
            self._info_response = data[:]

    def send(self, addr: str, param: Optional[str] = None):
        self.logger.debug(f"sending: {addr} {param if param is not None else ''}")
        self.server.send_message(addr, param)
        self._info_response = None
        time.sleep(self._delay)

    def query(self, address):
        self.send(address)
        return self.info_response

    def subscribe(self, callback_function):
        self._subscribe("/xremote", callback_function)

    def _subscribe(self, parameter_string, callback_function):
        self.subscription = threading.Thread(
            target=self._subscribe_worker,
            args=(
                parameter_string,
                callback_function,
            ),
            daemon=True,
        )
        self.subscription.start()

    def _subscribe_worker(self, parameter_string, callback_function, *other_params):
        self._callback_function = callback_function
        self.send(parameter_string)
        renew_string = "/renew"
        if parameter_string == "/xremote":
            renew_string = "/xremote"
        while self._callback_function:
            time.sleep(9)
            self.send(renew_string)
        return True

    def unsubscribe(self):
        self.send("/unsubscribe")
        self._callback_function = None
        return True

    def __exit__(self, exc_type, exc_value, exc_tr):
        self.server.shutdown()

    def state(self, key=None):
        # Return current mixer state
        if key:
            return self._state.get(key)
        return self._state

    def load_scene(self, scene_number):
        # Return current mixer state
        self.send(self.cmd_scene_load, scene_number)

    def reload(self):
        # Reload state
        self._state = {}
        self._load_initial()

    def _load_initial(self):
        # Load initial state
        expanded_addresses = []
        for address_row in self.addresses_to_load:
            address = address_row[0]
            rewrite_address = address_row[1] if len(address_row) > 1 else None
            matches = re.search(r"\{(.*?)(:(\d)){0,1}\}", address)
            if matches:
                match_var = matches.group(1)
                max_count = getattr(self, match_var)
                zfill_num = int(matches.group(3) or 0) or len(str(max_count))
                for number in range(1, max_count + 1):
                    new_address = address.replace(
                        "{" + match_var + "}", str(number).zfill(zfill_num)
                    )
                    expanded_addresses.append(new_address)
                    if rewrite_address:
                        new_rewrite_address = rewrite_address.replace(
                            "{" + match_var + "}", str(number).zfill(zfill_num)
                        )
                        self._rewrites[new_address] = new_rewrite_address
            else:
                expanded_addresses.append(address)
                if rewrite_address:
                    self._rewrites[address] = rewrite_address
        for address in expanded_addresses:
            self.send(address)

    def _update_state(self, address, values):
        # update internal state representation
        # State looks like
        #    /ch/02/mix_fader = Value
        #    /ch/02/config_name = Value
        rewrite_key = self._rewrites.get(address)
        if rewrite_key:
            address = rewrite_key
        state_key = self._generate_state_key(address)
        value = values[0]
        updates = []
        if state_key:
            if self._callback_function and state_key not in self._state:
                # we are processing updates and data captured is not in initial state
                # Therefore we want to ignore data
                return updates

            if state_key.endswith("_on"):
                value = bool(value)
            state_key = re.sub(r"/0+(\d+)/", r"/\1/", state_key)
            self._state[state_key] = value
            updates.append({"property": state_key, "value": value})
            if state_key.endswith("_fader"):
                db_val = fader_to_db(value)
                self._state[state_key + "_db"] = db_val
                updates.append({"property": state_key + "_db", "value": db_val})
        return updates

    @staticmethod
    def _generate_state_key(address):
        # generate a key for use by state from the address
        prefixes = [
            r"^/ch/\d+/",
            r"^/bus/\d+/",
            r"^/dca/\d+/",
            r"^/mtx/\d+/",
            r"^/main/[a-z]+/",
        ]
        for prefix in prefixes:
            match = re.match(prefix, address)
            if match:
                key_prefix = address[: match.span()[1]]
                key_string = address[match.span()[1] :]
                key_string = key_string.replace("/", "_")
                return key_prefix + key_string
        return address

    def _build_reverse_rewrite(self):
        # Invert the mapping for self._rewrites
        if not self._rewrites_reverse:
            self._rewrites_reverse = {v: k for k, v in self._rewrites.items()}

    def set_value(self, address, value):
        if address.endswith("_db"):
            address = address.replace("_db", "")
            value = db_to_fader(value)
        if value == False:
            value = 0
        if value == True:
            value = 1
        address = address.replace("_", "/")
        address = self._redo_padding(address)
        self._build_reverse_rewrite()
        rewrite_key = self._rewrites_reverse.get(address)
        if rewrite_key:
            address = rewrite_key
        self.send(address, value)
        self.query(address)
        # self._update_state(address, [value])

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
