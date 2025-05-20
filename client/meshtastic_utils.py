import logging

iface = None

def set_interface(interface):
    global iface
    iface = interface

def set_node_position(lat, lng):
    if iface:
        logging.info(f"Aggiorno posizione nodo: lat={lat}, lng={lng}")
        iface.localNode.setPosition(lat=lat, lon=lng)
