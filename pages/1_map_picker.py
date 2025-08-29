import streamlit as st
from datetime import datetime
import requests
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="Taxi Fare Map Picker", page_icon="🗺️", layout="wide")

st.title("🗺️ Taxi Fare Prediction with Map Picker")
st.markdown(
    """
    Select pickup and dropoff locations directly from the map  
    instead of entering coordinates manually.  
    """
)

# --- DEFAULTS ---
DEFAULTS = {
    "pickup_date_map": datetime.today().date(),
    "pickup_time_map": datetime.now().time(),
    "pickup_coords": None,
    "dropoff_coords": None,
    "passenger_count_map": 1,
}

# --- SESSION STATE INIT ---
for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

if "map_reset_counter" not in st.session_state:
    st.session_state.map_reset_counter = 0

# --- DATE & TIME ---
pickup_date = st.date_input("Pickup Date", st.session_state.pickup_date_map, key="pickup_date_map")
pickup_time = st.time_input("Pickup Time", st.session_state.pickup_time_map, key="pickup_time_map")

# --- MAP SELECTION ---
st.markdown("### 📍 Select Pickup & Dropoff on Map")
tab1, tab2 = st.tabs(["🚕 Pickup Location", "🏁 Dropoff Location"])

with tab1:
    m1 = folium.Map(location=[40.7128, -74.0060], zoom_start=12)
    st.markdown("Click on the map to select your **pickup location**.")
    map_data1 = st_folium(
        m1,
        height=400,
        width=700,
        returned_objects=["last_clicked"],
        key=f"pickup_map_{st.session_state.map_reset_counter}",  # dynamic key
    )
    if map_data1 and map_data1.get("last_clicked"):
        st.session_state.pickup_coords = map_data1["last_clicked"]
        st.success(f"📍 Pickup set to: {st.session_state.pickup_coords}")

with tab2:
    m2 = folium.Map(location=[40.7128, -74.0060], zoom_start=12)
    st.markdown("Click on the map to select your **dropoff location**.")
    map_data2 = st_folium(
        m2,
        height=400,
        width=700,
        returned_objects=["last_clicked"],
        key=f"dropoff_map_{st.session_state.map_reset_counter}",  # dynamic key
    )
    if map_data2 and map_data2.get("last_clicked"):
        st.session_state.dropoff_coords = map_data2["last_clicked"]
        st.success(f"🏁 Dropoff set to: {st.session_state.dropoff_coords}")

# --- PASSENGER COUNT ---
st.markdown("### 👥 Passengers")
passenger_count = st.number_input(
    "Passenger Count", min_value=1, max_value=8, step=1, key="passenger_count_map"
)

# --- TRIP SUMMARY ---
st.markdown("---")
st.subheader("📊 Trip Summary")
st.write(f"**Pickup:** {pickup_date} at {pickup_time}")
st.write(f"**Pickup Location:** {st.session_state.pickup_coords}")
st.write(f"**Dropoff Location:** {st.session_state.dropoff_coords}")
st.write(f"**Passengers:** {passenger_count}")

# --- API CALL ---
st.markdown("---")
st.subheader("🔮 Predict Taxi Fare")

url = "https://taxifare-786090284058.europe-west1.run.app/predict"

colA, colB = st.columns([1, 1])

with colA:
    predict_btn = st.button("🚀 Predict Fare")
with colB:
    reset_btn = st.button("🔄 Reset Inputs")

# --- RESET LOGIC ---
if reset_btn:
    for key in DEFAULTS.keys():
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.map_reset_counter += 1  # force new map widgets
    st.rerun()

# --- PREDICTION ---
if predict_btn:
    if not st.session_state.pickup_coords or not st.session_state.dropoff_coords:
        st.error("⚠️ Please select both pickup and dropoff points on the map.")
    else:
        params = {
            "pickup_datetime": f"{pickup_date} {pickup_time}",
            "pickup_longitude": st.session_state.pickup_coords["lng"],
            "pickup_latitude": st.session_state.pickup_coords["lat"],
            "dropoff_longitude": st.session_state.dropoff_coords["lng"],
            "dropoff_latitude": st.session_state.dropoff_coords["lat"],
            "passenger_count": passenger_count,
        }

        try:
            response = requests.get(url, params=params, timeout=30)
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