import logging
from db_utils import update_node_info
from meshtastic_utils import print_node_info

def on_connection(interface, **kwargs):
    """
    Callback chiamato alla connessione con il nodo Meshtastic.
    """
    logging.info("Connesso al nodo Meshtastic")
    print_node_info(interface)

    try:
        info = interface.myInfo
        if info:
            update_node_info(
                node_num=info.my_node_num,
                long_name=interface.localNode.getLongName(),
                short_name=interface.localNode.getShortName(),
                hw_model=interface.localNode.hwModel,
            )
        else:
            logging.warning("Info nodo non disponibile (myInfo is None)")
    except Exception as e:
        logging.error(f"Errore durante l'elaborazione della connessione: {e}")
