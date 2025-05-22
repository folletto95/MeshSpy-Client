import logging
import json

def print_node_info(iface):
    try:
        logging.info("Connesso al nodo Meshtastic")
        print(f"Owner: {iface.localNode.user.get('longName')} ({iface.localNode.user.get('shortName')})")
        print("My info:", json.dumps(iface.myInfo.asDict(), indent=2))
        print("Metadata:", json.dumps(iface.getRadioConfig()["deviceMetadata"], indent=2))
        print("Nodes in mesh:", json.dumps({k: v for k, v in iface.nodes.items()}, indent=2))
        logging.debug(f"iface.localNode: {iface.localNode}")
    except Exception as e:
        logging.warning(f"Errore stampa info nodo: {e}")
