import streamlit as st
import requests
import pandas as pd

API_URL = "http://65.108.42.157:8000/buildings/filter"

st.set_page_config(page_title="Solar Finder", layout="wide")

st.title("☀️ Solar Building Finder")

# -------------------------
# SIDEBAR
# -------------------------
st.sidebar.header("Filters")

city = st.sidebar.selectbox("City", ["dortmund", "bochum", "duesseldorf"])

kwp_min = st.sidebar.number_input("Min kWp", value=50)
kwp_max = st.sidebar.number_input("Max kWp", value=1000)

tilt_min = st.sidebar.number_input("Tilt Min (°)", value=0)
tilt_max = st.sidebar.number_input("Tilt Max (°)", value=50)

area_min = st.sidebar.number_input("Min Area", value=500)
area_max = st.sidebar.number_input("Max Area", value=5000)

distance_max = st.sidebar.number_input("Max Distance", value=500)

radiation_min = st.sidebar.number_input("Min Radiation", value=1000)
min_yield = st.sidebar.number_input("Min Yield", value=45000)

landuse = st.sidebar.multiselect(
    "Landuse",
    ["residential", "commercial", "industrial"],
    default=["commercial", "industrial"]
)

require_transformer = st.sidebar.checkbox("Require Transformer", True)
roof_orientation = st.sidebar.checkbox("South/West", True)
optimal_tilt = st.sidebar.checkbox("Optimal Tilt", True)

# -------------------------
# MAIN AREA (ALWAYS VISIBLE)
# -------------------------
st.info("👉 Select filters and click Search")

search = st.button("🔍 Search")

if search:

    payload = {
        "city": city,
        "kwp_min": kwp_min,
        "kwp_max": kwp_max,
        "tilt_min": tilt_min,
        "tilt_max": tilt_max,
        "area_min": area_min,
        "area_max": area_max,
        "distance_max": distance_max,
        "radiation_min": radiation_min,
        "min_yield": min_yield,
        "landuse": landuse,
        "require_transformer": require_transformer,
        "roof_orientation": roof_orientation,
        "optimal_tilt": optimal_tilt
    }

    with st.spinner("Calling API..."):
        try:
            response = requests.post(API_URL, json=payload, timeout=10)

            if response.status_code != 200:
                st.error(f"API error: {response.text}")
            else:
                result = response.json()

                if result["count"] == 0:
                    st.warning("No results found")
                else:
                    df = pd.DataFrame(result["data"])

                    st.success(f"{result['count']} buildings found")

                    st.dataframe(df)

        except Exception as e:
            st.error(f"Connection error: {e}")