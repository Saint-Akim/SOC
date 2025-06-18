import streamlit as st

def estimate_soc(voltage):
    soc =    [100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50,
              45, 40, 35, 30, 25, 20, 15, 10, 5, 0]
    volts = [810.0, 804.6, 800.7, 799.2, 798.0, 796.9, 795.8, 794.4,
             792.9, 790.7, 787.95, 786.8, 784.55, 782.3, 780.05, 777.8,
             775.55, 773.3, 771.05, 768.8, 766.55]

    for i in range(len(volts) - 1):
        if volts[i] >= voltage >= volts[i + 1]:
            v1, v2 = volts[i], volts[i + 1]
            s1, s2 = soc[i], soc[i + 1]
            estimated = s1 + ((voltage - v1) / (v2 - v1)) * (s2 - s1)
            return round(estimated, 2)
    return -1.0

st.set_page_config(page_title="Battery SoC Estimator", page_icon="🔋")
st.title("🔋 Battery SoC Estimator")

st.markdown("Enter your battery's **system voltage** below to estimate the current State of Charge (SoC).")

voltage = st.number_input("🔌 Voltage input (V)", min_value=760.0, max_value=820.0, step=0.1)

if st.button("⚡ Estimate SoC"):
    soc = estimate_soc(voltage)
    if soc >= 0:
        st.success(f"✅ Estimated SoC: **{soc:.2f}%**")
    else:
        st.error("⚠️ Voltage is outside the known safe range (766.55V – 810V). Please check input.")
