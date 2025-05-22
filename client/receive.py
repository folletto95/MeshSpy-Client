import logging
from pubsub import pub
from meshtastic_utils import on_receive, on_connection

def setup_receive(iface, server_url):
    pub.subscribe(lambda p, i=None: on_receive(p, i, server_url), "meshtastic.receive")
    pub.subscribe(lambda i, t=None: on_connection(i), "meshtastic.connection.established")
