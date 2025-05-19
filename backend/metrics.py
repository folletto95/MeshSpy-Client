from prometheus_client import Counter, Gauge

nodes_total = Gauge("meshspy_nodes_total", "Numero totale di nodi conosciuti")
nodes_with_gps = Gauge("meshspy_nodes_with_gps", "Nodi con coordinate GPS valide")
messages_received = Counter("meshspy_messages_received", "Totale messaggi MQTT ricevuti")
