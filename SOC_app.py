import streamlit as st
import threading
import paho.mqtt.client as mqtt


# Sidebar for MQTT connection input
st.sidebar.title("🔐 MQTT Settings")
broker = st.sidebar.text_input("Broker IP", value="192.168.2.98")
port = st.sidebar.number_input("Port", value=1883, step=1)
username = st.sidebar.text_input("Username", value="", type="default")
password = st.sidebar.text_input("Password", value="", type="password")

topics_input = st.sidebar.text_area("MQTT Topics (one per line)", value="\n".join([
    "solarmd/ES Control Service/SMDH81714700987",
    "solarmd/ES Control Service/SMDH89203995790",
    "solarmd/Plant Control/PC_9848495",
    "solarmd/ES Control Service/SMDH84684598460"
]))
topics = [line.strip() for line in topics_input.splitlines() if line.strip()]

start_connection = st.sidebar.button("🔌 Connect")

# Store data in session
if "mqtt_data" not in st.session_state:
    st.session_state.mqtt_data = {}
if "mqtt_status" not in st.session_state:
    st.session_state.mqtt_status = "Disconnected"
if "mqtt_thread_started" not in st.session_state:
    st.session_state.mqtt_thread_started = False


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        st.session_state.mqtt_status = "Connected ✅"
        for topic in topics:
            client.subscribe(topic, qos=0)
    else:
        st.session_state.mqtt_status = f"Failed to connect, rc={rc}"


def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode('utf-8')
        try:
            payload_val = float(payload)
        except:
            payload_val = payload
        st.session_state.mqtt_data[msg.topic] = payload_val
    except:
        pass


def mqtt_client_thread(broker, port, username, password):
    client = mqtt.Client(client_id="streamlit_mqtt_ui")
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, int(port), 60)
    client.loop_forever()


# Start thread if button clicked
if start_connection and not st.session_state.mqtt_thread_started:
    threading.Thread(
        target=mqtt_client_thread,
        args=(broker, port, username, password),
        daemon=True
    ).start()
    st.session_state.mqtt_thread_started = True
    st.session_state.mqtt_status = "Connecting..."


# App content
st.title("🔋 Battery SoC Estimator — MQTT UI Login")
st.write(f"MQTT Status: **{st.session_state.mqtt_status}**")

st.subheader("📡 Latest MQTT Data")
if st.session_state.mqtt_data:
    for topic, val in st.session_state.mqtt_data.items():
        st.write(f"**{topic}:** {val}")
else:
    st.write("⏳ Waiting for data...")
