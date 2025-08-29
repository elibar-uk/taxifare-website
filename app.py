import streamlit as st
from datetime import datetime
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="Taxi Fare Prediction", page_icon="🚖", layout="centered")

# --- HEADER ---
st.title("🚖 Taxi Fare Model Frontend")
st.markdown(
    """
    Welcome!  
    This app lets you simulate a taxi ride and input parameters to estimate the fare.  
    Use the controls below to set your trip details.  

    👉 For map-based location picking, go to **'Map Picker'** in the sidebar.
    """
)

# --- SESSION STATE FOR RESET ---
if "reset" not in st.session_state:
    st.session_state.reset = False

# --- INPUT SECTION ---
st.subheader("📝 Ride Details")

pickup_date = st.date_input("Pickup Date", datetime.today(), key="pickup_date")
pickup_time = st.time_input("Pickup Time", datetime.now().time(), key="pickup_time")

# Coordinates
st.markdown("### 📍 Pickup & Dropoff Coordinates")
col1, col2 = st.columns(2)

with col1:
    pickup_longitude = st.number_input("Pickup Longitude", format="%.6f", key="pickup_longitude")
    pickup_latitude = st.number_input("Pickup Latitude", format="%.6f", key="pickup_latitude")

with col2:
    dropoff_longitude = st.number_input("Dropoff Longitude", format="%.6f", key="dropoff_longitude")
    dropoff_latitude = st.number_input("Dropoff Latitude", format="%.6f", key="dropoff_latitude")

# Passenger count
st.markdown("### 👥 Passengers")
passenger_count = st.number_input("Passenger Count", min_value=1, max_value=8, step=1, key="passenger_count")

# --- DISPLAY SUMMARY ---
st.markdown("---")
st.subheader("📊 Trip Summary")
st.write(f"**Pickup:** {pickup_date} at {pickup_time}")
st.write(f"**Pickup Location:** ({pickup_latitude}, {pickup_longitude})")
st.write(f"**Dropoff Location:** ({dropoff_latitude}, {dropoff_longitude})")
st.write(f"**Passengers:** {passenger_count}")

# --- API CALL ---
st.markdown("---")
st.subheader("🔮 Predict Taxi Fare")

url = "https://taxifare-786090284058.europe-west1.run.app/predict"

colA, colB = st.columns([1,1])

with colA:
    predict_btn = st.button("🚀 Predict Fare")
with colB:
    reset_btn = st.button("🔄 Reset Inputs")

# --- RESET LOGIC ---
if reset_btn:
    for key in ["pickup_date","pickup_time","pickup_longitude","pickup_latitude","dropoff_longitude","dropoff_latitude","passenger_count"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# --- PREDICT LOGIC ---
if predict_btn:
    if (pickup_longitude == 0 or pickup_latitude == 0 or 
        dropoff_longitude == 0 or dropoff_latitude == 0 or 
        passenger_count <= 0):
        st.error("⚠️ Please provide valid non-zero values for all fields before predicting.")
    else:
        params = {
            "pickup_datetime": f"{pickup_date} {pickup_time}",
            "pickup_longitude": pickup_longitude,
            "pickup_latitude": pickup_latitude,
            "dropoff_longitude": dropoff_longitude,
            "dropoff_latitude": dropoff_latitude,
            "passenger_count": passenger_count
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                prediction = response.json().get("fare", None)
                if prediction is not None:
                    st.metric(label="💵 Estimated Fare", value=f"${prediction:,.2f}")
                else:
                    st.warning("No fare value returned by the API.")
            else:
                st.error(f"API request failed with status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {e}")