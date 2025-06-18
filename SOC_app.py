!pip install paho-mqtt
import streamlit as st
import threading
import paho.mqtt.client as mqtt
import time


MQTT_BROKER = "192.168.2.98"
MQTT_PORT = 1883
MQTT_USERNAME = "mqtt"
MQTT_PASSWORD = "V0yant!Aut0"  


MQTT_TOPICS = [
    "solarmd/ES Control Service/SMDH81714700987",
    "solarmd/ES Control Service/SMDH89203995790",
    "solarmd/Plant Control/PC_9848495",
    "solarmd/ES Control Service/SMDH84684598460"
]

# Store latest payloads here
if "mqtt_data" not in st.session_state:
    st.session_state.mqtt_data = {}

# Store connection status
if "mqtt_status" not in st.session_state:
    st.session_state.mqtt_status = "Disconnected"

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        st.session_state.mqtt_status = "Connected ✅"
        for topic in MQTT_TOPICS:
            client.subscribe(topic, qos=0)  # QoS 0 for least overhead (read-only)
    else:
        st.session_state.mqtt_status = f"Failed to connect, rc={rc}"

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode('utf-8')
        # Try converting to float if possible
        try:
            payload_val = float(payload)
        except:
            payload_val = payload

        st.session_state.mqtt_data[msg.topic] = payload_val
    except Exception as e:
        pass  # Ignore errors silently

# MQTT client in a separate thread
def mqtt_client_thread():
    client = mqtt.Client(client_id="readonly_soc_estimator")  # unique client id, read-only
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    # Connect and loop forever
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

# Start MQTT client thread once
if "mqtt_thread_started" not in st.session_state:
    threading.Thread(target=mqtt_client_thread, daemon=True).start()
    st.session_state.mqtt_thread_started = True
    st.session_state.mqtt_status = "Connecting..."

# Display connection status
st.title("🔋 Battery SoC Estimator — MQTT Read-Only")
st.write(f"MQTT Status: **{st.session_state.mqtt_status}**")

# Display incoming MQTT data live for debugging and mapping
st.subheader("Latest MQTT Data Received")
if st.session_state.mqtt_data:
    for topic, val in st.session_state.mqtt_data.items():
        st.write(f"**{topic}:** {val}")
else:
    st.write("No data received yet...")
