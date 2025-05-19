from opcua import Server, ua
import random
import time

server = Server()
server.set_endpoint("opc.tcp://0.0.0.0:4841/source/")
server.set_server_name("SourceServer")

uri = "http://example.org/sourceserver/"
idx = server.register_namespace(uri)

objects = server.get_objects_node()
device = objects.add_object(idx, "SimulatedDevice")

temp_node = device.add_variable(idx, "MotorTemperature", 80.0)
temp_node.set_writable()

server.start()
print("[INFO] Serveur source lancé à : opc.tcp://localhost:4841/source/")

try:
    while True:
        new_value = random.uniform(80, 100)
        temp_node.set_value(ua.Variant(new_value, ua.VariantType.Double))
        # print(f"[INFO] Nouvelle température moteur : {new_value:.2f} °C")
        time.sleep(1)

except KeyboardInterrupt:
    print("[INFO] Arrêt du serveur source...")
    server.stop()
