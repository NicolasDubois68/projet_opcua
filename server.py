import xml.etree.ElementTree as ET
from opcua import Server, Client, ua
import time

def load_mappings(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    mappings = []
    for var in root.findall("variable"):
        source = var.find("source").text
        mapped_name = var.find("mapped_name").text
        mappings.append((source, mapped_name))
    return mappings

client = Client("opc.tcp://localhost:4841/source/")
client.connect()
print("[INFO] Connecté au serveur source")

mappings = load_mappings("mapping_config.xml")

server = Server()
server.set_endpoint("opc.tcp://0.0.0.0:4840/mapped/")
server.set_server_name("MappedServer")

uri = "http://example.org/mymappedserver/"
idx = server.register_namespace(uri)

objects = server.get_objects_node()
mapped_obj = objects.add_object(idx, "MappedVariables")

client_nodes = {}
server_nodes = {}

for source_id, mapped_name in mappings:
    client_node = client.get_node(source_id)
    server_node = mapped_obj.add_variable(idx, mapped_name, 0.0)
    server_node.set_writable()
    client_nodes[mapped_name] = client_node
    server_nodes[mapped_name] = server_node

server.start()
print("[INFO] Serveur Mappé lancé à : opc.tcp://localhost:4840/mapped/")
print("[INFO] Variables mappées disponibles :")
for name in server_nodes:
    print(f" - {name}")

try:
    while True:
        for name in server_nodes:
            value = client_nodes[name].get_value()
            server_nodes[name].set_value(ua.Variant(value, ua.VariantType.Double))
            # print(f"[INFO] {name} : {value:.2f}")
        time.sleep(1)

except KeyboardInterrupt:
    print("[INFO] Arrêt du serveur mappé...")
finally:
    client.disconnect()
    server.stop()
