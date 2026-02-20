import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

# --- PART 1: AUTO-TRAIN THE MODEL (Ensures app works immediately) ---
def train_initial_model():
    # Creating synthetic physics-based data if no dataset exists
    np.random.seed(42)
    rows = 2000
    temp = np.random.uniform(2, 45, rows)
    hum = np.random.uniform(30, 90, rows)
    vib = np.random.uniform(0.1, 1.2, rows)
    
    # Physics Rule: Decay doubles every 10°C above 4°C
    decay_rate = 2 ** ((temp - 4) / 10)
    # Mechanical Rule: Vibration > 0.5G adds 1.5x multiplier
    decay_rate = np.where(vib > 0.5, decay_rate * 1.5, decay_rate)
    
    days_left = np.clip(10 / decay_rate, 0, 14) # Max 14 days
    
    X = pd.DataFrame({'Temperature': temp, 'Humidity': hum, 'Vibration': vib})
    y = days_left
    
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, y)
    joblib.dump(model, 'spoilage_model.pkl')
    return model

if os.path.exists('spoilage_model.pkl'):
    model = joblib.load('spoilage_model.pkl')
else:
    model = train_initial_model()

# --- PART 2: UI SETUP ---
st.set_page_config(page_title="Aegis Harvest | Command Center", layout="wide")

# Custom CSS for that "Logistics" look
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #4e5d6c; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Aegis Harvest: Spoilage Shield")
st.subheader("Predictive Supply Chain Dashboard")

# --- PART 3: SIDEBAR & CHAOS BUTTON ---
st.sidebar.header("🚛 Truck ID: AG-8829")
st.sidebar.divider()

# The "Chaos Button" - This is your codeathon requirement
chaos_mode = st.sidebar.toggle("🚨 SIMULATE COOLING FAILURE", help="Triggers Crisis State")

if chaos_mode:
    # Danger Range
    st.sidebar.warning("CRITICAL: Cooling System Offline")
    temp = st.sidebar.slider("Ambient Temp (°C)", 30, 50, 42)
    vib = st.sidebar.slider("Road Vibration (G)", 0.6, 2.0, 1.1)
    hum = st.sidebar.slider("Humidity (%)", 80, 100, 92)
else:
    # Safe Range
    st.sidebar.success("Status: Normal Operations")
    temp = st.sidebar.slider("Reefer Temp (°C)", 2, 8, 4)
    vib = st.sidebar.slider("Road Vibration (G)", 0.1, 0.4, 0.2)
    hum = st.sidebar.slider("Humidity (%)", 50, 70, 62)

# --- PART 4: ML INFERENCE ---
# Predict Days_Left based on live slider values
prediction = model.predict([[temp, hum, vib]])[0]

# --- PART 5: SMART REROUTE ENGINE ---
# Mock Logistics Data
centers = {
    "Original": {"dist": 120, "road": "Clear", "cap": 45},
    "Center A": {"dist": 35, "road": "Blocked", "cap": 80}, # Blocked road test
    "Center B": {"dist": 55, "road": "Smooth", "cap": 95}   # High capacity test
}

def calculate_best_center(shelf_life):
    best_center = "Original"
    max_sm = -999
    results = []
    
    for name, info in centers.items():
        # Travel time: 50km/h avg. Convert to Days.
        travel_time = (info['dist'] / 50) / 24
        
        # Logic 1: Blocked Roads
        if info['road'] == "Blocked":
            travel_time = 999 
        
        # Logic 2: Capacity Penalty (>90% full adds 6 hours)
        if info['cap'] > 90:
            travel_time += 0.25
            
        # Logic 3: Survival Margin (SM)
        sm = shelf_life - travel_time
        results.append({"Center": name, "Survival Margin (Days)": round(sm, 2), "Capacity": f"{info['cap']}%"})
        
        if sm > max_sm:
            max_sm = sm
            best_center = name
            
    if max_sm < 0: return "🗑️ DUMP CARGO", results
    return best_center, results

best_dest, reroute_table = calculate_best_center(prediction)

# --- PART 6: MAIN DASHBOARD DISPLAY ---
col1, col2, col3 = st.columns(3)

# Metrics with dynamic delta colors
col1.metric("Live Temperature", f"{temp}°C", delta=f"{temp-4}°C" if temp > 4 else None, delta_color="inverse")
col2.metric("Vibration Stress", f"{vib} G", delta="HIGH" if vib > 0.5 else "LOW", delta_color="inverse")
col3.metric("Predicted Shelf Life", f"{prediction:.2f} Days")

st.divider()

# Visual Feedback
if prediction < 2 or chaos_mode:
    st.error(f"🚨 CRITICAL ALERT: Rerouting initiated to: **{best_dest}**")
else:
    st.success(f"✅ Route Optimized: Heading to **{best_dest}**")

# Displaying the Decision Logic
st.subheader("Smart Reroute Logic Matrix")
st.dataframe(pd.DataFrame(reroute_table), use_container_width=True)

# Footer
st.caption("Aegis Harvest v1.0 | Real-time Spoilage Mitigation Engine")