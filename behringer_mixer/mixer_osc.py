from typing import Optional, Union
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_message_builder import OscMessageBuilder
from pythonosc.osc_server import BlockingOSCUDPServer


class OSCClientServer(BlockingOSCUDPServer):
    def __init__(self, address: str, dispatcher: Dispatcher):
        super().__init__(("", 0), dispatcher)
        self.mixer_address = address

    def send_message(self, address: str, vals: Optional[Union[str, list]]):
        builder = OscMessageBuilder(address=address)
        vals = vals if vals is not None else []
        if not isinstance(vals, list):
            vals = [vals]
        for val in vals:
            builder.add_arg(val)
        msg = builder.build()
        self.socket.sendto(msg.dgram, self.mixer_address)
