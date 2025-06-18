import streamlit as st

# --- Battery Configurations ---
BATTERY_CAPACITY_KWH = 215.0
MAX_CELL_VOLTAGE = 3.375     # at 100% SoC
MIN_CELL_VOLTAGE = 3.205     # at 10% SoC
MAX_PACK_VOLTAGE = 54.0      # at 100% SoC
MIN_PACK_VOLTAGE = 51.28     # at 10% SoC
MAX_SYSTEM_VOLTAGE = 810.0   # at 100% SoC
MIN_SYSTEM_VOLTAGE = 769.20  # at 10% SoC

# --- Exact measured system voltage-to-SoC data ---
voltage_soc_data = {
    810.00: 100,
    804.60: 95,
    800.70: 90,
    799.20: 85,
    798.00: 80,
    796.90: 75,
    795.80: 70,
    794.40: 65,
    792.90: 60,
    790.70: 55,
    787.95: 50,
    786.80: 45,
    784.55: 40,
    782.30: 35,
    780.05: 30,
    777.80: 25,
    775.55: 20,
    773.30: 15,
    771.05: 10,
    768.80: 5,
    766.55: 0
}

# --- Streamlit UI ---
st.set_page_config(page_title="Advanced Battery SoC Estimator", page_icon="🔋")
st.title("🔋 Advanced Battery SoC Estimator")
st.markdown("Enter known battery measurements to get the most accurate SoC.")

# --- Inputs ---
system_voltage = st.number_input("System Voltage (V)", min_value=760.0, max_value=820.0, step=0.01)
cell_voltage = st.number_input("Average Cell Voltage (V)", min_value=3.0, max_value=3.5, step=0.001)
pack_voltage = st.number_input("Pack Voltage (V)", min_value=50.0, max_value=60.0, step=0.01)
actual_energy_remaining = st.number_input("Actual Remaining Energy (kWh)", min_value=0.0, max_value=BATTERY_CAPACITY_KWH, step=0.1)
energy_used = st.number_input("Energy Used So Far (kWh, optional)", min_value=0.0, max_value=BATTERY_CAPACITY_KWH, step=0.1)
current = st.number_input("Average Current (A, optional)", min_value=0.0, step=0.01)
uptime = st.number_input("Uptime (hours, optional)", min_value=0.0, step=0.01)

# --- Optional Cell-Level Diagnostics ---
min_cell_voltage = st.number_input("Min Cell Voltage (V, optional)", min_value=2.0, max_value=4.0, step=0.001)
max_cell_voltage = st.number_input("Max Cell Voltage (V, optional)", min_value=2.0, max_value=4.0, step=0.001)

# --- SoC Estimation Functions ---
def interpolate_soc(voltage, min_v, max_v, min_soc=10, max_soc=100):
    return max(min_soc, min(max_soc, (voltage - min_v) / (max_v - min_v) * (max_soc - min_soc) + min_soc))

def system_voltage_soc_lookup(voltage):
    return voltage_soc_data[min(voltage_soc_data.keys(), key=lambda v: abs(v - voltage))]

# --- Estimations ---
soc_system_voltage_interp = interpolate_soc(system_voltage, MIN_SYSTEM_VOLTAGE, MAX_SYSTEM_VOLTAGE, min_soc=10)
soc_system_voltage_table = system_voltage_soc_lookup(system_voltage)
soc_cell_voltage = interpolate_soc(cell_voltage, MIN_CELL_VOLTAGE, MAX_CELL_VOLTAGE, min_soc=10)
soc_pack_voltage = interpolate_soc(pack_voltage, MIN_PACK_VOLTAGE, MAX_PACK_VOLTAGE, min_soc=10)
soc_energy_remaining = (actual_energy_remaining / BATTERY_CAPACITY_KWH) * 100 if actual_energy_remaining > 0 else None
soc_energy_used = (1 - (energy_used / BATTERY_CAPACITY_KWH)) * 100 if energy_used > 0 else None
soc_from_current = None
if current > 0 and uptime > 0:
    estimated_energy = (system_voltage * current * uptime) / 1000  # in kWh
    soc_from_current = (1 - (estimated_energy / BATTERY_CAPACITY_KWH)) * 100

# --- Combine Available SoC Estimates ---
estimates = [soc_system_voltage_interp, soc_system_voltage_table, soc_cell_voltage, soc_pack_voltage]
if soc_energy_remaining is not None: estimates.append(soc_energy_remaining)
if soc_energy_used is not None: estimates.append(soc_energy_used)
if soc_from_current is not None: estimates.append(soc_from_current)
final_soc = round(sum(estimates) / len(estimates), 2)

# --- Display ---
if st.button("🔎 Estimate SoC"):
    st.markdown(f"### 🧮 Estimated SoC: **{final_soc}%**")
    st.write("**Based on:**")
    st.write(f"- System Voltage SoC (Table): {soc_system_voltage_table}%")
    st.write(f"- System Voltage SoC (Interpolated): {soc_system_voltage_interp:.2f}%")
    st.write(f"- Cell Voltage SoC: {soc_cell_voltage:.2f}%")
    st.write(f"- Pack Voltage SoC: {soc_pack_voltage:.2f}%")
    if soc_energy_remaining is not None:
        st.write(f"- Remaining Energy SoC: {soc_energy_remaining:.2f}%")
    if soc_energy_used is not None:
        st.write(f"- Energy Used SoC: {soc_energy_used:.2f}%")
    if soc_from_current is not None:
        st.write(f"- Current-based SoC: {soc_from_current:.2f}%")

    # Diagnostic Warnings
    if max_cell_voltage > 0 and min_cell_voltage > 0:
        delta_mv = (max_cell_voltage - min_cell_voltage) * 1000
        st.info(f"📉 Cell Voltage Imbalance: {delta_mv:.2f} mV")
        if delta_mv > 20:
            st.warning("⚠️ High cell voltage imbalance detected.")
